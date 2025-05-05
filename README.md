Testing:

install extention: Python Test Explorer for Visual Studio code

run: pip install pytest

Test with: python -m pytest [relative path]

Debug:
1. Set breakpoint
2. Go to the run and debug section on the left of VS
3. Select "Pytest" at the top 
If you don't see Pytest, create a new configuration which should be in blue highlighted text and copy and paste:
"configurations": [
        {
            "name": "Pytest",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Python Debugger: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
4. Go to the file you want to debug and run the debug by using the play button on the run and debug tab