aws-hcs-cli
Python script for CLI and SDK access to AWS via ADFS while requiring MFA access using https://duo.com/

History and Purpose
Harman used to use "the Legendary" aws-adfs CLI tool to login to our AWS accounts. It worked great, especially the DUO 2FA support. Eventually, I decided to write my own similar tool but make it Harman-specific so that we could tailor it to our needs. Since this tool will be used by Harman employees only I had that option. I then morphed it a little more for our use cases.

DUO 2FA Requirements
In order for Duo 2FA to work properly Automatic Push needs to be enabled.

Installation
Python 3.6+ is recommended as python2 is EOL January 2020.
It is highly recommended to use an application like Pipx to install and use python cli applications.
Follow the pipx installation documentation then simply run pipx install aws-hcs-cli
Experimental Binaries are available on the releases page. These are new and in testing Releases
See the installation options For additional options page for step by step instructions for installing in various environments
