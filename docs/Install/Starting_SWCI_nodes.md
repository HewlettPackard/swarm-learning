# <a name="GUID-BAEEFDBA-FC5E-40BC-89B8-0B7BC738B8D3"/> Starting SWCI nodes

Use the `swarm-learning/bin/run-swci` to launch SWCI. The SWCI command prompt is displayed when the launch is successful. You can enter any command from a pre-defined set of commands. It supports a list of well-defined commands that are self-explanatory. There is a built-in online help, that lists all supported commands and further one can drill down and see help for each command.

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

|Parameter name|Description|Default value|
|--------------|-----------|-------------|
|`--usr-dir <dir>`|The host directory that must be used as the user directory by this SWCI node.|None|
|`--init-script-name <swci-init file>`|Name of `swci-init` file. This file must be located inside the user directory at the top level.|`swci-init`|

