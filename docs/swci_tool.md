# Swarm Learning Command Interface (SWCI)

SWCI is the command interface tool to the Swarm Learning framework. It is used to view the status, control and manage the Swarm Learning framework. SWCI manages Swarm Learning framework using Contexts and Contracts.

## Context

A SWCI tool can control operations on multiple Swarm Learning framework instances. Each instance is encapsulated and represented as a *context*. At a given time, only *one context is active*. All SWCI commands work with the current active context (default context) and they do not take context as an explicit argument. Users are required to explicitly create a context (using the CREATE context command) and activate it as shown below

    +---------------------------------------------------------------------+
    | SWCI:13 > create context **testContext** sn.test.sw.net             |
    |                                                                     |
    | API Server is UP!                                                   |
    |                                                                     |
    | CONTEXT CREATED : **testContext**                                   |
    |                                                                     |
    | SWCI:14 > SWITCH CONTEXT testContext                                |
    |                                                                     |
    | DEFAULT CONTEXT SET TO : testContext                                |
    |                                                                     |
    | SWCI:15 >                                                           |
    +---------------------------------------------------------------------+

Commands related to contexts:

-   CREATE CONTEXT \<contextName:string> \<ip:string> \[port:string\]

    -   Creates a new SWCI context.

    -   contextName is a user given identifier for this context.

    -   \"ip\" is the IP addr or FQDN of the SN Node

    -   \"port\" (Optional) is the port number on which the SN node's
    API-Server is Listening

-   SWITCH CONTEXT \<contextName:string>

    -   Switches current SWCI context to specified one

-   LIST CONTEXTS

    -   Prints list of Contexts this SWCI session has.

-   GET CONTEXT INFO \<contextName: string>

    -   Prints context information of the current Context, if
        contextName is not specified

    -   If contextName is specified prints information for the specified
        context

-   LIST CONTEXT ENV \<contextName:string>

    -   Displays the list of context specific environment variables.

    -   contextName: specifies the context from which these
        environmental variables will be listed.

-   SET CONTEXT ENV \<contextName:string> \<env:string> \<envValue:string>

    -   Sets the value of the specified context specific environmental
        variable.

    -   contextName: specifies the name of the target context.

    -   env: specifies the target environmental variable within the
        context.

    -   envValue: value for the variable being set.

-   GET CONTEXT ENV \<contextName:string> \<env:string>

    -   Gets the value of the specified context specific environmental
        variable.

    -   contextName: specifies the name of the target context.

    -   env: specifies the target environmental variable within the
        context.

-   GET CONTEXT VERSION

    -   Returns the API Server\'s versioning Information

## Contract

Swarm Learning training contracts are used to control the swarm learning training process. It is an instance of a *smart contract*. It is deployed into the blockchain and registered into Swarm Learning Network using CREATE CONTRACT command.

Commands related to contracts:

-   LIST CONTRACTS

    -   Displays the list of Swarm Learning Contracts currently registered
    into the Swarm Learning Network

-   GET CONTRACT INFO \<SLContractName:string>

    -   Displays static information about the specified SL Contract

-   GET CONTRACT STATUS \<SLContractName:string>

    -   Reports the current status of the specified SL Contract

-   RESET CONTRACT \<SLContractName:string>

    -   Resets the state of the contract to uninitialized state.

    -   **WARNING:** This action cannot be undone, Reset only completed SL
    Contracts. Resetting active contracts can results in unexpected
    behavior.

-   CREATE CONTRACT \<SLContractName:string>
    -   Registers the specified SL Contract into the Swarm Learning Network

## Other commands in SWCI

-   WAIT FOR \<ip:string> \[port:string\] \[retries:string\]

    -   Waits for the specified API-SERVER to accept Connections.

    -   ip: is the IP addr or FQDN of the API-SERVER (Swarm Network Node) serving Swarm Learning APIs.

    -   port: (Optional) is string representation of the port number on
        which the API-Server is listening.

    -   retries: (Optional). Default \"retries\" is 360 times (30 Mins).
        This is the maximum number of times SWCI will re-attempt to
        connect after waiting for 5 Sec timeout period.

-   EXIT

    -   This command exits the SWCI session unconditionally

-   EXIT ON FAILURE \[ON/OFF\]

    -   This command instructs SWCI to exit the current session when any
        of the subsequent command fails

    -   Default is OFF
