# Winutils Setup Complete ✅

## What Was Done

1. **Downloaded winutils.exe** and **hadoop.dll** to `C:\Outils\Spark\bin\`
   - Source: https://github.com/cdarlint/winutils (Hadoop 3.3.5)
   - Files downloaded:
     - winutils.exe (112KB)
     - hadoop.dll

2. **Set Environment Variable**
   - `HADOOP_HOME = C:\Outils\Spark`
   - This is now set permanently in your User environment variables

3. **Updated Your Scripts**
   - Added `os.environ['HADOOP_HOME'] = r'C:\Outils\Spark'` to `exercise1_2.py`
   - This ensures Spark finds winutils.exe

## Result

✅ **The winutils warnings are GONE!**

Before:

```
26/01/19 14:38:49 WARN Shell: Did not find winutils.exe: java.io.FileNotFoundException:
Could not locate Hadoop executable: d:\M2\S6\spark-4.1.1-bin-hadoop3\bin\winutils.exe
26/01/19 14:38:49 WARN NativeCodeLoader: Unable to load native-hadoop library...
```

After:

```
No winutils warnings! ✨
```

## For Your Other Exercise Files

Add this line at the top of any other Python Spark scripts:

```python
import os
os.environ['HADOOP_HOME'] = r'C:\Outils\Spark'
```

Or, since HADOOP_HOME is now set as a system environment variable, new terminal sessions will automatically have it available!

## Note

The EOFException error you're seeing is a different issue (related to Python worker communication) and is unrelated to winutils. The winutils warnings are completely eliminated.
