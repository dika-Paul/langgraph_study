using System;
using System.Diagnostics;
using System.IO;
using System.Text;

internal static class Program
{
    private static int Main(string[] args)
    {
        Process current = Process.GetCurrentProcess();
        if (current.MainModule == null || string.IsNullOrEmpty(current.MainModule.FileName))
        {
            throw new InvalidOperationException("Unable to resolve wrapper path.");
        }

        string selfPath = current.MainModule.FileName;
        string selfDir = Path.GetDirectoryName(selfPath);
        if (string.IsNullOrEmpty(selfDir))
        {
            throw new InvalidOperationException("Missing wrapper directory.");
        }

        string realPath = Path.Combine(selfDir, Path.GetFileNameWithoutExtension(selfPath) + ".real.exe");

        if (!File.Exists(realPath))
        {
            Console.Error.WriteLine("Missing real executable: " + realPath);
            return 127;
        }

        Environment.SetEnvironmentVariable("HTTP_PROXY", "http://127.0.0.1:7897");
        Environment.SetEnvironmentVariable("HTTPS_PROXY", "http://127.0.0.1:7897");
        Environment.SetEnvironmentVariable("ALL_PROXY", "socks5://127.0.0.1:7898");
        Environment.SetEnvironmentVariable("NO_PROXY", "localhost,127.0.0.1,::1");

        var startInfo = new ProcessStartInfo(realPath)
        {
            UseShellExecute = false,
            WorkingDirectory = Environment.CurrentDirectory,
        };

        startInfo.Arguments = BuildArguments(args);

        Process child = Process.Start(startInfo);
        if (child == null)
        {
            throw new InvalidOperationException("Failed to launch " + realPath);
        }

        try
        {
            child.WaitForExit();
            return child.ExitCode;
        }
        finally
        {
            child.Dispose();
        }
    }

    private static string BuildArguments(string[] args)
    {
        var builder = new StringBuilder();

        for (int i = 0; i < args.Length; i++)
        {
            if (i > 0)
            {
                builder.Append(' ');
            }

            builder.Append('"');
            builder.Append(args[i].Replace("\\", "\\\\").Replace("\"", "\\\""));
            builder.Append('"');
        }

        return builder.ToString();
    }
}
