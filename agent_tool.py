from typing import Type, Optional, Any

import aiohttp
import requests
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from env_config import load_env_config




ENV_CONFIG = load_env_config()




class IPModel(BaseModel):
    ip_address: str = Field(description='IP地址')


class IPLocationByGaoDe(BaseTool):
    name: str = 'IPLocationByGaoDe'
    description: str = '当需要根据ip获取位置时，调用此工具'
    args_schema: Type[IPModel] = IPModel
    return_direct: bool = True

    gaode_api_key: Optional[str] = ENV_CONFIG['gaode_api_key']
    gaode_base_url: Optional[str] = ENV_CONFIG['gaode_base_url']


    def _gaode_config_judge(self) -> bool:
        return self.gaode_api_key is None or self.gaode_base_url is None

    def get_session_kwargs(self, ip_address: str) -> dict:
        return {
            'url': f'{self.gaode_base_url}ip={ip_address}&key={self.gaode_api_key}',
            'headers': {'Content-Type': 'application/json; charset=utf-8'},
        }

    @staticmethod
    def response_analysis(res: Any) -> str:
        if str(res.get('status')) == '0':
            return f'查询失败：{res.get('info', '未知错误')}'

        if not res.get('province') and not res.get('city'):
            return '无法查询此ip信息'

        return f'{res.get("province")}, {res.get("city")}'


    def _run(self, ip_address: str) -> str:
        if self._gaode_config_judge():
            raise ValueError('高德配置不完善')

        session_kwargs = self.get_session_kwargs(ip_address)
        session_kwargs['timeout'] = 20

        resp = requests.get(**session_kwargs)
        resp.raise_for_status()
        res = resp.json()

        return self.response_analysis(res)


    async def _arun(self, ip_address: str) -> str:
        if self._gaode_config_judge():
            raise ValueError('高德配置不完善')

        session_kwargs = self.get_session_kwargs(ip_address)
        session_kwargs['timeout'] = aiohttp.ClientTimeout(total=20)

        async with aiohttp.ClientSession() as session:
            async with session.get(**session_kwargs) as resp:
                resp.raise_for_status()
                res = await resp.json()

        return self.response_analysis(res)




class SearchQueryModel(BaseModel):
    query: str = Field(description='执行搜索的询问语句')


class SearchQueryByBoCha(BaseTool):
    name: str = 'SearchQueryByBoCha'
    description: str = '需要获取实时内容时，调用此工具'
    args_schema: Type[SearchQueryModel] = SearchQueryModel
    return_direct: bool = True

    bocha_api_key: Optional[str] = ENV_CONFIG['bocha_api_key']
    bocha_base_url: Optional[str] = ENV_CONFIG['bocha_base_url']


    def _bocha_config_judge(self) -> bool:
        return self.bocha_api_key is None or self.bocha_base_url is None

    def get_session_kwargs(self, query: str) -> dict:
        return {
            'url': f'{self.bocha_base_url}',
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Authorization': f'Bearer {self.bocha_api_key}',
            },
            'json': {
                'query': query,
                'summary': True,
                'count': 9
            },
        }

    @staticmethod
    def response_analysis(res: Any) -> str:
        if str(res.get('code')) != '200':
            return f'请求错误：{res.get('message')}'

        web_pages = res.get('data', {}).get('webPages', {}).get('value', [])

        if not web_pages:
            return '查询不到相关信息'

        formatted_web_pages = []
        for index, web_page in enumerate(web_pages, start=1):
            formatted_web_page = '\n'.join([
                f'id: {index}',
                f'网页标题: {web_page.get('name')}',
                f'网址: {web_page.get('url')}',
                f'内容描述: {web_page.get('snippet')}',
                f'内容摘要: {web_page.get('summary')}',
            ])
            formatted_web_pages.append(formatted_web_page)

        return '\n\n'.join(formatted_web_pages)


    def _run(self, query: str) -> str:
        if self._bocha_config_judge():
            raise ValueError('博查配置错误')

        session_kwargs = self.get_session_kwargs(query)
        session_kwargs['timeout'] = 20

        resp = requests.post(**session_kwargs)
        resp.raise_for_status()
        res = resp.json()

        return self.response_analysis(res)


    async def _arun(self, query: str) -> str:
        if self._bocha_config_judge():
            raise ValueError('博查配置错误')

        session_kwargs = self.get_session_kwargs(query)
        session_kwargs['timeout'] = aiohttp.ClientTimeout(total=20)

        async with aiohttp.ClientSession() as session:
            async with session.post(**session_kwargs) as resp:
                resp.raise_for_status()
                res = await resp.json()

        return self.response_analysis(res)


