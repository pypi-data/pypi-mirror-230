# LPDB
> Python debug configuration generator for vscode

## Install

```shell script
pip install lpdb
```

## Command Line Tools

### lpdb 
VSCode debug configuration generator from a python command line.

It can automatically generate the debug configuration file for vscode by just adding `lpdb` in front of your python command.
It will parse the environment variables and the arguments list correctly.

For example:
```shell
lpdb CUDA_VISIBLE_DEVICES=1,2 python train.py --batch-size 16 --lr 1e-4
```

It will generate the debug configuration in `.vscode/launch.json`. 
Then you can debug your python file by clicking the corresponding button.

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: python train.py --batch-size 16 --lr 1e-4",
            "type": "python",
            "request": "launch",
            "program": "train.py",
            "env": {
                "CUDA_VISIBLE_DEVICES": "1,2"
            },
            "console": "integratedTerminal",
            "args": [
                "--batch-size",
                "16",
                "--lr",
                "1e-4"
            ],
            "cwd": "/home/xxx/demo_project"
        }
    ]
}
```



1. This repo based on vpdb:https://github.com/silverbulletmdc/vpdb
2. Support torchrun