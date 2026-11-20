using System;

class Program
{
    static int Main(string[] args)
    {
        // Act like winutils
        if (args.Length > 0 && args[0] == "ls")
        {
             // basic mock for ls if needed, for permissions usually implies "dwrx..."
             // But for chmod it just needs to exit 0
             // If Spark calls ls to check permissions, we might need to output something.
             // For checkoint creation, it calls mkdirs which calls chmod.
             return 0;
        }
        return 0;
    }
}
