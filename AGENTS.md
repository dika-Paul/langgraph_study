# Python Interpreter Rule

Any command in this project that needs Python must use the exact interpreter
below. Do not use `python`, `py`, or rely on the active shell environment.

Fixed interpreter:

```powershell
D:\SoftWare\Anaconda\envs\deeplearning\python.exe
```

## Command Templates

Run the main script:

```powershell
& "D:\SoftWare\Anaconda\envs\deeplearning\python.exe" .\main.py
```

Run any Python file:

```powershell
& "D:\SoftWare\Anaconda\envs\deeplearning\python.exe" .\path\to\script.py
```

Install dependencies:

```powershell
& "D:\SoftWare\Anaconda\envs\deeplearning\python.exe" -m pip install -r .\requirements.txt
```

Run a module:

```powershell
& "D:\SoftWare\Anaconda\envs\deeplearning\python.exe" -m package.module
```

Start Jupyter:

```powershell
& "D:\SoftWare\Anaconda\envs\deeplearning\python.exe" -m notebook
```

## Notes

- In PowerShell, use `&` to invoke the executable path.
- Apply the same interpreter path in IDE settings, tasks, scripts, and CI.
- Keep this rule for any future Python-related command added to the project.
