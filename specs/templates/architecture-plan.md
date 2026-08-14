# Architecture plan — {SPEC-ID}

How the specification maps onto modules, ports and adapters.

## Bounded context

_Which bounded context does this belong to?_

## Diagram

```mermaid
flowchart TB
    subgraph inbound["Inbound adapters"]
    end
    subgraph app["Application"]
    end
    subgraph domain["Domain"]
    end
    subgraph outbound["Outbound adapters"]
    end
    BOOT["Bootstrap"]
```

## Module decomposition

### Java

| Module | Depends on |
| --- | --- |

### Python

```
src/{context}/{domain,application,adapters,bootstrap}
```

## Ports

| Port | Direction | Why it exists |
| --- | --- | --- |

## Mapping across boundaries

_How domain, DTO and persistence representations relate._

## Fitness functions

| Rule | Java | Python |
| --- | --- | --- |

## Impact

_New code, changed code, build time, rollback strategy._
