# hcs-cli Cheatsheet

- [hcs-cli Cheatsheet](#hcs-cli-cheatsheet)
  - [Specify Org ID](#specify-org-id)
  - [Utility Commands](#utility-commands)
    - [Profile Commands](#profile-commands)
    - [Login Commands](#login-commands)
    - [Context Commands](#context-commands)
      - [Text Template with Context Variables](#text-template-with-context-variables)
    - [Plan Commands](#plan-commands)
  - [Service Commands](#service-commands)
    - [Admin](#admin)
    - [VmHub](#vmhub)
    - [PKI](#pki)
    - [LCM](#lcm)


## Specify Org ID
Many HCS APIs requires org ID. There are three ways to specify org ID:

1. Default from authentication info. If not specified, the org ID from the current authentication info will be used. E.g.:
   ```
   hcs admin template list
   ```
   To view the org info of the current authentication info, do:
   ```
   hcs login -d
   ```
2. Specify org ID explicitly:
   ```
   hcs admin template list --org <my-org-id>
   ```
3. Specify org ID via environment variable:
   ```
   export HCS_ORG=<my-org-id>
   hcs admin template list
   ```

## Utility Commands

### Profile Commands
* Profile is a configuration for the target HCS environment you want to access, with the API token or client ID/credential for authentication.
* HCS CLI has the "profile" subcommand to manage multiple profiles.
* All HCS CLI commands works with the "current" profile, which can be changed via the profile subcommand.
* Profiles are nothing but files in ~/.hcs/profiles. You may also edit the files directly.

| Example                                | Purpose                                |
|----------------------------------------|----------------------------------------|
| hcs profile init	                     | Initialize a default profile. |
| hcs profile init --name \<name\>       | Initialize a profile with a custom name. | 
| hcs profile list	                     | List existing profiles. |
| hcs profile get [name]	             | Get the current profile, or a specific profile by name. |
| hcs profile use        	             | Show an interactive view to select from profiles. |
| hcs profile use \<name\>	             | Switch to a profile. |
| hcs profile delete \<name\>            | Delete a profile. |
| hcs profile edit                 | Edit the current profile file directly. |
| hcs profile file [name]              | Show the file path of a profile, current or by name. So you can use the file directly. |
| hcs profile copy -f \<name1\> -t \<name2\> | Copy a profile. |

### Login Commands

The login command works with the current profile and will update the current profile. If no token is specified, a browser will be launched to login interactively.

| Example                                | Purpose                                |
|----------------------------------------|----------------------------------------|
| hcs login                              | Login with configured credentials, otherwise do an interactive login using browser. |
| hcs login -d                         | Get authentication details. |
| hcs login --api-token \<csp-api-token\> | Programmatically login with CSP API token. |
| hcs login --client-id \<client-id\> --client-secret \<client-secret\> | Programmatically login with OAuth client id/secret. |


### Context Commands
* Context is a state store backed by disk files. Context is associated with a profile. Different profiles have different contexts. Context is for supporting automation. E.g. the authentication state is cached using context.
* Context is similar to the environment variable, and context template utility is like the envsubst command. The difference is, context is persisted and can be reused.
* Context is internally used to support some complex subcommands which has orchestration and has the need to support break-and-resume.

| Example                                | Purpose                                |
|----------------------------------------|----------------------------------------|
| hcs context clear                      | Delete all context objects, for the current profile.
| hcs context list                       | List all context item names, for the current profile. |
| hcs context get                        | Get data of a specific context object, for the current profile. |
| hcs context set                        | Set a context object by name, for the current profile. |
| hcs context delete                     | Delete a context object by name, for the current profile. |

#### Text Template with Context Variables

The CLI framework provides a utility to facilitate template-based processing, with context variables. So in an automation scenario, downstream operations can easily access results from upstream operations, by sharing the states stored in the context.

There are two scenarios:

In side HCS CLI command implementation, context is accessible.
In a script that uses HCS CLI, the "hcs context" command can be used to access the context values.

### Plan Commands

Plan is a resource management engine, which deploy/destroy resources using a blueprint.

| Example                                | Purpose                                |
|----------------------------------------|----------------------------------------|
| hcs plan apply -f \<plan-file-name\>  | Deploy resources according to a plan. |
| hcs plan destroy -f \<plan-file-name\> | Delete all resources related to a plan. |
| hcs plan graph -f \<plan-file-name\> | View resource dependency graph in a plan. |


## Service Commands

### Admin
| Example                                | Purpose                                |
|----------------------------------------|----------------------------------------|
| hcs admin edge list                    | List edges. |
| hcs admin edge get \<id\>              | Get a specific edge by ID. |
| hcs admin template list --template-search "providerLocation $eq westus2" | List templates by query. | 
| hcs admin template get \<id\>          | Get a template by ID. |

### VmHub
| Example                                | Purpose                                |
|----------------------------------------|----------------------------------------|
| hcs vmhub otp request                  |  Request a one-time-password for a resource              |
| hcs vmhub otp redeem                   | Redeem a one-time-password for a resource certificate         |


### PKI
| Example                                | Purpose                                |
|----------------------------------------|----------------------------------------|
| hcs pki sign-resource-cert my-res1     | Request a resource certificate. |
| hcs pki get-root-ca                    | Get root CA configured for the target environment. |
| hcs pki get-org-cert                   | Get the org signing CA. |
| hcs pki delete-org-cert                | Delete org signing CA. A new one will be created again when needed. |
### LCM

| Purpose                                                    | Example                                |
|------------------------------------------------------------|----------------------------------------|
| hcs lcm template create --id-only < payload/lcm/zero.json            | Create a zerocloud template for test. |
| hcs lcm template wait \<id\>                  | Wait for template ready. |
| hcs lcm template wait --timeout=1m10s --return-template \<id\>  | Wait for template ready. |
| hcs lcm template list --type ZEROCLOUD \| jq ".\|map(.id)" | List all zerocloud templates, id only. |
| hcs lcm template list --org=all --limit=2000  | List templates from all orgs (requires service global read permission). |
| hcs lcm template get \<id\>                   | Get template by ID. |
| hcs lcm template delete \<id\>                | Delete template by ID. |
| hcs lcm provider list --type ZEROCLOUD                     | List zero providers. |
| hcs lcm provider get \<id\>                   | Get a provider by ID. |
| hcs lcm provider delete \<id\>                | Delete a provider by ID. |
