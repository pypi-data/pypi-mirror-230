<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

This package provides a unified command line interface to Atgenomix SeqsLab, a cloud-native biomedical informatics (BioMed IT) platform.

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#install-the-seqslab-cli">Install the SeqsLab CLI</a> </li>
        <li><a href="#interactive-mode">Interactive Mode</a></li>
        <li><a href="#cli-mode">CLI Mode</a></li>
        <li><a href="#basic-commands">Basic Commands</a></li>
      </ul>
    <li><a href="#getting-help">Getting Help</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#more-resources">More Resources</a></li>
  </ol>
</details>

## Getting Started

### Prerequisites

* Python 3.8 or later
 
* [keyring](https://pypi.org/project/keyring/)
* [dbus](https://wiki.freedesktop.org/www/Software/dbus/)
* [glib](https://docs.gtk.org/glib/)
* [pkg-config](https://freedesktop.org/wiki/Software/pkg-config/)


Detail to see [Installation](https://github.com/atgenomix/seqslab-cli/wiki/Installation)

### Install the SeqsLab CLI
  ```bash
  pip install seqslab-cli
  ```

### Interactive Mode

This mode provides fish-style auto-completion functionality that is user-friendly, especially for beginners.

* Run interactive mode.
  ```bash
  seqslab
  ```

* Display the available commands.
  ```bash
  root> help
  ```

* End the current interactive mode session and return to the Linux shell.
  ```bash
  root> exit
  ```
  
### CLI Mode

Through the use of subcommands, you can operate the SeqsLab CLI like any traditional Linux-based command-line utility.

  ```bash
  seqslab -h

  seqslab auth -h
  ```

### Basic Commands
#### Authentication with the SeqsLab API

Regardless of the mode that you intend to use, you must sign in to authenticate the session. The SeqsLab CLI follows the OAuth 2.0 Device Authorization Grant (external URL) process.  

Example (interactive mode):

* Specify the platform backend to be used when launching the SeqsLab CLI. The default value is `azure`.

  ```bash
  seqslab --backend azure
  ```

* Sign in to the SeqsLab API and obtain API tokens with a single command. By default, the sign-in process uses the Authorization Code Flow.

  ```bash
  root> auth signin
  ```

  Set the device-code argument to `True`. By default, the sign-in command uses the Device Code Flow for browserless systems.

  ```bash
  root>  auth signin device-code=True
  ```

* Obtain an API access token for interacting with SeqsLab API apps.

  ```bash
  root> auth token
  # use token in your request header, ex: Authorization: Bearer {access}
  ```

  Access tokens are persistently cached in the system-supported secret service (for example, Freedesktop Secret Service or macOS Keychain). As a result, valid access tokens can be used across multiple SeqsLab CLI sessions.
#### Help documentation
To view help documentation, use one of the following:

```bash
root> help
```

## Getting Help
The best way to interact with our team is through GitHub. You can open an issue and choose from one of our templates for guidance, bug reports, or feature requests.

Please check for open similar issues before opening another one.

## More Resources

* [SeqsLab CLI Documentation](https://docs.atgenomix.com/tutorials/cli.html)

## Contributing

The repository currently does not accept contributions but will eventually be opened to the community.


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-url]: https://github.com/AnomeGAP/seqslab-cli/graphs/contributors

[stars-url]: https://github.com/AnomeGAP/seqslab-cli/stargazers

[issues-url]: https://github.com/AnomeGAP/seqslab-cli/issues

[license-url]: https://github.com/AnomeGAP/seqslab-cli/blob/main/LICENSE.txt

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555

[linkedin-url]: https://www.linkedin.com/company/atgenomix

[product-screenshot]: https://github.com/AnomeGAP/seqslab-cli/blob/main/Atgenomix%20SeqsLab%20V3.png
