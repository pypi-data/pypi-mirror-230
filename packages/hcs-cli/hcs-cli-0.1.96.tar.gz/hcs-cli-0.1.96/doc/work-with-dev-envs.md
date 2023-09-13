# Work with Development Environments

By default, HCS CLI is configured to use production environment. To work with a custom development environment:

Create profiles for development environments:
```
hcs profile init --dev
```

Switch between profiles:
```
hcs profile use
```

Next we need to authenticate. There are three approaches:

| Example                                | Purpose                                |
|----------------------------------------|----------------------------------------|
| hcs login [--org \<csp-org-id\>]             | Login with configured credentials, otherwise do an interactive login using browser. If your CSP default org is not the org for HCS, --org argument must be specified.|
| hcs login --api-token \<csp-api-token\> | Login with CSP API token. Reference: [Get CSP User API Token](doc/get-csp-user-api-token.md). |
| hcs login --client-id \<client-id\> --client-secret \<client-secret\> [--org \<org-id\>] | Login with OAuth client id/secret. |

Alternatively, you may directly edit the current profile to specify api-token, or client-id/secret:
```
hcs profile edit
```

By default, profiles for common developments are created. To create a custom profile, either for using a different auth identity, or for using a feature stack, copy the profile;

```
hcs profile copy --from \<src-name\> --to \<target-name>
hcs profile edit
```

The authentication token will be cached. In case of debugging of authentication:

Option 1: logout and login again.

```
hcs logout
hcs login
```

Option 2: do an OAuth token refresh, using the refresh token.

```bash
hcs login --refresh
```