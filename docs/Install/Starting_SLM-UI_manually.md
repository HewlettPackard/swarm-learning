# Starting SLM-UI manually 

SLM-UI containers are automatically started by the SLM-UI installer. But, if it is not running on the host, users need to manually start it using the following commands.

1.  Initially, run `<swarm-learning>/slm-ui/scripts/run-postgres -pw" supersecretpassword"` \(default DB password, unless you have changed the default password of the database using external tools like pgAdmin\).

2.  Then, run `<swarm-learning>/slm-ui/scripts/run-slm-ui`. Most of the other arguments of the above commands are optional. If you have changed the defaults, then you can use the following arguments to specify them.

The following arguments are the optional arguments for `run-postgres`:

|Argument|Description|
|--------|-----------|
|`-d|--data <dir>`

|Directory where DB data will be persisted to default: /opt/hpe/swarm-learning/slm-ui/data

|
|`-u|--user <string>`

|Postgres database username.

 default: `postgres`

|
|`-pw|--password <string>`

|Postgres database password.

|
|`-po|--port <number>`

|Postgres database port.

 default: 5432

|
|`-n|--network <string>`

|Docker network where database and SLM-UI communicate.

 default: `slm-ui-network`

|
|`-h|--help|/h`

|help

|

The following arguments are the optional arguments for `run-slm-ui`:

|Argument|Description|
|--------|-----------|
|`-nw|--network <name>`

|Docker network where SLM-UI and database communicate.

 default: `slm-ui-network`

|
|`-l|--log <dir>`

|Directory where log files will be saved to.

 default: `./logs`

|
|`-pu|--public-cert <name>`

|Public Certificate Name.

|
|`-pr|--private-cert <name>`

|Private Certificate Name.

|
|`-ca|--ca-cert <name>`

|Certificate Authority Certificate Name.

|
|`-h|--help|/h`

|help

|

**Parent topic:**[Installing HPE Swarm Learning Management UI \(SLM-UI\)](GUID-60017971-B0A9-4119-AEAF-A21594EE5C1E.md)

