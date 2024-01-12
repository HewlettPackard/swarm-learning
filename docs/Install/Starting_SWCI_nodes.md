# <a name="GUID-BAEEFDBA-FC5E-40BC-89B8-0B7BC738B8D3"/> Starting SWCI nodes

Use the `swarm-learning/scripts/bin/run-swci` to launch SWCI. The SWCI command prompt is displayed when the launch is successful. You can enter any command from a pre-defined set of commands. It supports a list of well-defined commands that are self-explanatory. There is a built-in online help, that lists all supported commands and further one can drill down and see help for each command.

```
SWCI:2 > help HELP
HELP [command:string]
Help without parameter lists all supported commands.
Help with command name show help content for the specified command.
SWCI:3 >
```

<blockquote>
  
NOTE: You must launch the SWCI node after the SN nodes are started.

</blockquote>

The run-swci script accepts the following parameters:

|Parameter name &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |Description|Default value &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;  |
|--------------|-----------|-------------------------------------------------------|
|`--usr-dir <dir>`|The host directory that must be used as the user directory by this SWCI node.|None|
|`--init-script-name <swci-init file>`*|Name of the init script file that has SWCI commands to be executed at the start of SWCI. <br> This file must be located inside the user directory at the top level.<br>|`swci-init`|

*If init script option is provided, all SWCI commands within this script file are processed before it enters the interactive mode and waits for users commands. Users can simulate a non-interactive SWCI run by having a bunch of SWCI commands and an SWCI `EXIT` command at the end of the `swci-init` file. This could be used for automation.

<blockquote>
  
NOTE: 
- If you need to use the swci-init script file as-is (default), --usr-dir option must be specified and SWCI looks for this default script file under this user  directory.
- If you want to run a script file with a different filename, you must explicitly specify the --init-script-name
and --usr-dir.
- If the --usr-dir is not specified, the SWCI runs in an interactive mode.

</blockquote>
