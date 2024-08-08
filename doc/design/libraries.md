# Libraries

| Name                     | Description |
|--------------------------|-------------|
| *libpingvincoin_cli*         | RPC client functionality used by *pingvincoin-cli* executable |
| *libpingvincoin_common*      | Home for common functionality shared by different executables and libraries. Similar to *libpingvincoin_util*, but higher-level (see [Dependencies](#dependencies)). |
| *libpingvincoin_consensus*   | Stable, backwards-compatible consensus functionality used by *libpingvincoin_node* and *libpingvincoin_wallet*. |
| *libpingvincoin_crypto*      | Hardware-optimized functions for data encryption, hashing, message authentication, and key derivation. |
| *libpingvincoin_kernel*      | Consensus engine and support library used for validation by *libpingvincoin_node*. |
| *libpingvincoinqt*           | GUI functionality used by *pingvincoin-qt* and *pingvincoin-gui* executables. |
| *libpingvincoin_ipc*         | IPC functionality used by *pingvincoin-node*, *pingvincoin-wallet*, *pingvincoin-gui* executables to communicate when [`--enable-multiprocess`](multiprocess.md) is used. |
| *libpingvincoin_node*        | P2P and RPC server functionality used by *pingvincoind* and *pingvincoin-qt* executables. |
| *libpingvincoin_util*        | Home for common functionality shared by different executables and libraries. Similar to *libpingvincoin_common*, but lower-level (see [Dependencies](#dependencies)). |
| *libpingvincoin_wallet*      | Wallet functionality used by *pingvincoind* and *pingvincoin-wallet* executables. |
| *libpingvincoin_wallet_tool* | Lower-level wallet functionality used by *pingvincoin-wallet* executable. |
| *libpingvincoin_zmq*         | [ZeroMQ](../zmq.md) functionality used by *pingvincoind* and *pingvincoin-qt* executables. |

## Conventions

- Most libraries are internal libraries and have APIs which are completely unstable! There are few or no restrictions on backwards compatibility or rules about external dependencies. An exception is *libpingvincoin_kernel*, which, at some future point, will have a documented external interface.

- Generally each library should have a corresponding source directory and namespace. Source code organization is a work in progress, so it is true that some namespaces are applied inconsistently, and if you look at [`libpingvincoin_*_SOURCES`](../../src/Makefile.am) lists you can see that many libraries pull in files from outside their source directory. But when working with libraries, it is good to follow a consistent pattern like:

  - *libpingvincoin_node* code lives in `src/node/` in the `node::` namespace
  - *libpingvincoin_wallet* code lives in `src/wallet/` in the `wallet::` namespace
  - *libpingvincoin_ipc* code lives in `src/ipc/` in the `ipc::` namespace
  - *libpingvincoin_util* code lives in `src/util/` in the `util::` namespace
  - *libpingvincoin_consensus* code lives in `src/consensus/` in the `Consensus::` namespace

## Dependencies

- Libraries should minimize what other libraries they depend on, and only reference symbols following the arrows shown in the dependency graph below:

<table><tr><td>

```mermaid

%%{ init : { "flowchart" : { "curve" : "basis" }}}%%

graph TD;

pingvincoin-cli[pingvincoin-cli]-->libpingvincoin_cli;

pingvincoind[pingvincoind]-->libpingvincoin_node;
pingvincoind[pingvincoind]-->libpingvincoin_wallet;

pingvincoin-qt[pingvincoin-qt]-->libpingvincoin_node;
pingvincoin-qt[pingvincoin-qt]-->libpingvincoinqt;
pingvincoin-qt[pingvincoin-qt]-->libpingvincoin_wallet;

pingvincoin-wallet[pingvincoin-wallet]-->libpingvincoin_wallet;
pingvincoin-wallet[pingvincoin-wallet]-->libpingvincoin_wallet_tool;

libpingvincoin_cli-->libpingvincoin_util;
libpingvincoin_cli-->libpingvincoin_common;

libpingvincoin_consensus-->libpingvincoin_crypto;

libpingvincoin_common-->libpingvincoin_consensus;
libpingvincoin_common-->libpingvincoin_crypto;
libpingvincoin_common-->libpingvincoin_util;

libpingvincoin_kernel-->libpingvincoin_consensus;
libpingvincoin_kernel-->libpingvincoin_crypto;
libpingvincoin_kernel-->libpingvincoin_util;

libpingvincoin_node-->libpingvincoin_consensus;
libpingvincoin_node-->libpingvincoin_crypto;
libpingvincoin_node-->libpingvincoin_kernel;
libpingvincoin_node-->libpingvincoin_common;
libpingvincoin_node-->libpingvincoin_util;

libpingvincoinqt-->libpingvincoin_common;
libpingvincoinqt-->libpingvincoin_util;

libpingvincoin_util-->libpingvincoin_crypto;

libpingvincoin_wallet-->libpingvincoin_common;
libpingvincoin_wallet-->libpingvincoin_crypto;
libpingvincoin_wallet-->libpingvincoin_util;

libpingvincoin_wallet_tool-->libpingvincoin_wallet;
libpingvincoin_wallet_tool-->libpingvincoin_util;

classDef bold stroke-width:2px, font-weight:bold, font-size: smaller;
class pingvincoin-qt,pingvincoind,pingvincoin-cli,pingvincoin-wallet bold
```
</td></tr><tr><td>

**Dependency graph**. Arrows show linker symbol dependencies. *Crypto* lib depends on nothing. *Util* lib is depended on by everything. *Kernel* lib depends only on consensus, crypto, and util.

</td></tr></table>

- The graph shows what _linker symbols_ (functions and variables) from each library other libraries can call and reference directly, but it is not a call graph. For example, there is no arrow connecting *libpingvincoin_wallet* and *libpingvincoin_node* libraries, because these libraries are intended to be modular and not depend on each other's internal implementation details. But wallet code is still able to call node code indirectly through the `interfaces::Chain` abstract class in [`interfaces/chain.h`](../../src/interfaces/chain.h) and node code calls wallet code through the `interfaces::ChainClient` and `interfaces::Chain::Notifications` abstract classes in the same file. In general, defining abstract classes in [`src/interfaces/`](../../src/interfaces/) can be a convenient way of avoiding unwanted direct dependencies or circular dependencies between libraries.

- *libpingvincoin_crypto* should be a standalone dependency that any library can depend on, and it should not depend on any other libraries itself.

- *libpingvincoin_consensus* should only depend on *libpingvincoin_crypto*, and all other libraries besides *libpingvincoin_crypto* should be allowed to depend on it.

- *libpingvincoin_util* should be a standalone dependency that any library can depend on, and it should not depend on other libraries except *libpingvincoin_crypto*. It provides basic utilities that fill in gaps in the C++ standard library and provide lightweight abstractions over platform-specific features. Since the util library is distributed with the kernel and is usable by kernel applications, it shouldn't contain functions that external code shouldn't call, like higher level code targeted at the node or wallet. (*libpingvincoin_common* is a better place for higher level code, or code that is meant to be used by internal applications only.)

- *libpingvincoin_common* is a home for miscellaneous shared code used by different Pingvincoin Core applications. It should not depend on anything other than *libpingvincoin_util*, *libpingvincoin_consensus*, and *libpingvincoin_crypto*.

- *libpingvincoin_kernel* should only depend on *libpingvincoin_util*, *libpingvincoin_consensus*, and *libpingvincoin_crypto*.

- The only thing that should depend on *libpingvincoin_kernel* internally should be *libpingvincoin_node*. GUI and wallet libraries *libpingvincoinqt* and *libpingvincoin_wallet* in particular should not depend on *libpingvincoin_kernel* and the unneeded functionality it would pull in, like block validation. To the extent that GUI and wallet code need scripting and signing functionality, they should be get able it from *libpingvincoin_consensus*, *libpingvincoin_common*, *libpingvincoin_crypto*, and *libpingvincoin_util*, instead of *libpingvincoin_kernel*.

- GUI, node, and wallet code internal implementations should all be independent of each other, and the *libpingvincoinqt*, *libpingvincoin_node*, *libpingvincoin_wallet* libraries should never reference each other's symbols. They should only call each other through [`src/interfaces/`](../../src/interfaces/) abstract interfaces.

## Work in progress

- Validation code is moving from *libpingvincoin_node* to *libpingvincoin_kernel* as part of [The libpingvincoinkernel Project #27587](https://github.com/pingvincoin/pingvincoin/issues/27587)
