

This is an implementation of [Context Programming](https://github.com/nanw1103/context-programming), for CLI program.

This implementation has the following configuration data structure, to support:
- Multiple command line tools in the same OS.
- Multiple profiles per tool.
- Context (and other context-like collections) per profile.

```
<repo-path>
    <cli-name-1>
        .state      # CLI specific global runtime state
        <profile-name-11>
            profile.yml
            context
                <application-specific-data-111>.yml
                <application-specific-data-112>.yml
            <other profile store 1>
                <file11>
            <other profile store 2>
                <file21>
                <file22>
        <profile-name-12>.yml
        ...
    <cli-name-2>
        ... # The same structure as cli-name-1
    ...
```

The default repo-path is: <user-home-dir>/<cli-name>
Take two different CLI programs _helloctl_ and _kittyctl_ as examples. Each of them may have multiple environments. By default the structure will be:

```
~
    helloctl
        .state
        default
            profile.yml
            context
                my-data11.yml
                my-data12.yml
        my-hello-env1
            profile.yml
            context
                my-data21.yml
        my-hello-env2
            profile.yml
            context <empty>
    kittyctl
        .state
        default
            profile.yml
        my-kitty-env
            context
                my-data1.yml
```

