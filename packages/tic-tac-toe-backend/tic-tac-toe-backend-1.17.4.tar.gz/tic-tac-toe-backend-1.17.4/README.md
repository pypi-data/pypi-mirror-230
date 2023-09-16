# tic-tac-toe-backend

<!-- Start SDK Installation -->
## SDK Installation

```bash
pip install tic-tac-toe-backend
```
<!-- End SDK Installation -->

## SDK Example Usage
<!-- Start SDK Example Usage -->


```python
import tic_tac_toe_backends


s = tic_tac_toe_backends.TicTacToeBackends()


res = s.get_()

if res.body is not None:
    # handle response
```
<!-- End SDK Example Usage -->

<!-- Start SDK Available Operations -->
## Available Resources and Operations

### [TicTacToeBackends SDK](docs/sdks/tictactoebackends/README.md)

* [get_](docs/sdks/tictactoebackends/README.md#get_) - Root endpoint.
* [get_version](docs/sdks/tictactoebackends/README.md#get_version) - Root endpoint.
* [put_games](docs/sdks/tictactoebackends/README.md#put_games) - Games endpoint. Creates the next game state from the previous game state.
<!-- End SDK Available Operations -->

### Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

### Contributions

While we value open-source contributions to this SDK, this library is generated programmatically.
Feel free to open a PR or a Github issue as a proof of concept and we'll do our best to include it in a future release!

### SDK Created by [Speakeasy](https://docs.speakeasyapi.dev/docs/using-speakeasy/client-sdks)
