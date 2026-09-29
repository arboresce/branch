# Branch UI Foundation v1

Status: owner-approved target specification, 2026-09-28. Implementation and
qualification are not complete. This specification owns the shared UI target;
[runtime state](runtime-state.md), [native artifacts](native-artifacts.md) and
[repository layout](repository-layout.md) retain their existing responsibilities.
Execution is recorded in the [BDS-00 plan](../execution/ui-foundation/bds-00-contracts.md)
and its linked sequence, not inferred from acceptance of this document.

## Scope and decisions

Deliver one reusable Compose Multiplatform UI for Android and iOS: all 92 entries
in [the component contract](../../contracts/ui-components.json), all ten entries
in [the service contract](../../contracts/platform-services.json), a separate
development catalog and three deterministic workflows. Preserve the Rust runtime,
application identity, Android API 28, iOS 18 and the existing target architectures.
Preserve the current iPad device-family declaration and qualify adaptive simulator
layouts. Desktop/web targets and new product features are outside this foundation.

Approved visual direction: Arboresce colors, Inter, Lucide, shared dimensions,
selective glass and accessible opaque fallbacks. English is the initial language;
long-text, bidirectional and RTL fixtures are required without claiming additional
translated product languages. Current qualification uses Android emulators and
iOS simulators. Physical Android and iPhone qualification remains required later.

Approved persistence: retain theme/effects preferences; restore allowlisted safe
navigation during OS-managed recreation; start at the root on a fresh launch;
tab re-selection preserves its stack. Passwords, codes and unfinished form contents
must never be written to disk. In-memory edit buffers may survive tab switching
but are disposed with their owning entry. No database or account synchronization
is introduced for these preferences.

No backend, account authentication, payments, analytics, production link domain,
remote flags, rich-text editor, maps, full video player, store distribution or
external package publication is included. Fixture Home/Search/Settings routes
are catalog examples, not a product roadmap. The runtime diagnostic remains a
real consumer until separately specified product screens replace it.

## Ownership and modules

| Location | Responsibility | Forbidden responsibility |
| --- | --- | --- |
| `core/domain`, `core/runtime`, `app/rust/runtime-ffi` | Existing Rust state, lifecycle and native facade | Presentation tokens, shaders or navigation stacks |
| `app/ui/design-system` | Typed theme, resources, controls, semantics, internal glass renderer | Product routes, repositories, ViewModels, permission requests |
| `app/ui/patterns` | Scaffolds, async/collection/modal patterns, `AppAsyncImage` | Global navigation or business rules |
| `app/platform` | Service contracts and lifecycle-safe Android/iOS implementations | Alternate app-owned UI rendering |
| `app/shared/app` | Common application root, presentation assembly, navigation/serialization | Duplicate Rust domain authority |
| `app/shared/xc-framework` | Minimal Swift-facing controller/update bridge | Exporting every internal Kotlin type |
| `app/catalog` | Development consumer, component examples and fixture workflows | Production dependency or production data |
| Existing hosts and diagnostic module | Native handle ownership, OS integration and real runtime consumer | Parallel product screen trees |

Gradle identities must be explicit and source packages must match directories.
Keep the existing UI and Rust framework boundaries; no forced framework merger.
Use constructor injection or existing assembly conventions. No empty model/data
modules, new DI framework or API/implementation module proliferation is required.
Platform objects must not enter persistent common UI state. Kotlin presentation
projections and edit state do not create a second domain model.

## BUI-01: Native integrity

Native cohort identity must describe the effective build, including supported
environment overrides. Normalize or reject undeclared build-affecting inputs;
do not hash an entire host environment or retain credentials. Changing
`CARGO_PROFILE_RELEASE_OPT_LEVEL` must change identity or fail explicitly.
`IPHONEOS_DEPLOYMENT_TARGET` must be normalized to the contract or rejected when
inconsistent; it must not silently reuse a different build. Include applicable
target flags, selected SDK/configuration and toolchain inputs in the policy.
Invalidate incompatible old cohort schemas without silently repairing them.

Only the cohort-root `manifest.json` is excluded from output-byte enumeration.
Nested files with that basename are ordinary outputs. Reject missing, modified,
unexpected and symlinked artifacts. Regression fixtures must reproduce both the
configuration-identity and nested-manifest failures and demonstrate correction.

## BUI-02: Build and resource delivery

Resolve compatible pinned Navigation 3, Backdrop, Coil, resources and test APIs
before committing to their integration. Preserve valid existing toolchain pins;
record any necessary change with Android/iOS compilation and consumer evidence.
Retain locks, verification metadata and the existing formatter conventions.

Explicit command routing must select platform, architecture and configuration,
including the correct Compose framework and resource bundle. Preserve existing
Make entry points and document new ones only after they exist. Add actual shared
test runners and simulator Release configurations; a Rust release library alone
does not make the UI a Release build. Device support must be prepared without
inventing signing identities or committing provisioning material.

Setup prepares the selected Python environment; checks reject unprepared or
stale environments with actionable diagnostics and do not repair them. New
checks must work from an independent checkout using documented public tools and
committed resources. A declaration of `commonTest` without executed tests fails.

Verification commands release only emulator processes they started, using bounded
shutdown/termination and preserving caller-owned targets. Preserve the primary
test failure if teardown also fails. Passing assertions do not make the complete
command green when cleanup fails or leaves its owned process running.

Resource installation validates the selected app and every existing destination
ancestor before deletion/copy. A lexical app-relative path is insufficient when
an intermediate directory is a symlink. Reject symlinked source trees, escaping
destinations and required inputs without regular resource files. The command that
mutates the bundle must enforce this policy, with outside-app sentinel tests.

## BUI-03: Reactive shared root

Both hosts render shared loading, sanitized error and content presentation.
Maintain a stable Compose controller on iOS and update observable state rather
than capture one initial snapshot or recreate the navigation tree. Native adapters
own runtime handles and off-main-thread calls; the common root receives immutable
results and typed presentation phases. Preserve selectable/scrollable diagnostic
content and its runtime smoke assertions. A synthetic fake may exercise successive
updates; no unsupported Rust event API or background polling is required.

Cancel disposed work, reject stale completions and avoid duplicate lifecycle loads.
Cancellation may permit a later explicit load; disposal is terminal. A cancelled
generation must not clear another generation's active state or permit overlapping
native calls. Native calls that cannot be interrupted must remain serialized until
they return, with obsolete results discarded. Each host and the catalog must own
and release controller work explicitly; a controller-owned scope is cancelled on
disposal without cancelling an externally supplied host scope. Retry from error
enters loading and suppresses duplicate activation. Prove these transitions with
controlled in-flight work and with visible updates in the same hosted UI instance.
An inactive/background owner cancels its request and resumes with one explicit
load when active again. A transient view disappearance is not terminal disposal
of an owner that will be reused. Terminal disposal follows owner removal; host and
catalog implementations must make that lifetime explicit and test resumption.
Concurrency tests must preserve the host's serialized controller ownership while
running blocking native fakes on a separate worker. Bound every wait and guarantee
worker release and scope cleanup on assertion failure or timeout. Owner-removal
tests must detect omitted disposal through observable work/results, not merely
wait for a phase that both disposed and undisposed controllers can reach.
Cancellation is not a user-visible failure. Components receive state and callbacks;
they do not access runtime handles. Verify successive iOS updates, shared error
presentation, recreation and disposal without losing unrelated navigation state.

## BUI-04: Theme and resources

Consume complete committed typed values, fonts, icons and notices. Ordinary builds
must not require another checkout or an unpublished generator. Generated outputs
are not independently editable palettes. Any source-format adapter must preserve
one authoritative value per token and reject missing references, alias cycles,
invalid units and inconsistent mode roles. Spatial dimensions become Dp and font
metrics become Sp; a standard typography-composite line-height multiplier must
not be confused with an absolute line-height dimension.

| Domain | Approved baseline |
| --- | --- |
| Brand | Primary `#a8a2f9`, blue `#5b7cfa`, background `#1c1e22`; semantic suitability must be checked |
| Spacing | 0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64 dp |
| Padding | Compact screen 16; relaxed 24; ordinary container 16; related gaps 8–12; section gaps 24–32 |
| Controls | Minimum target 48 by 48; nominal minimum button height 52; field height 56; all grow for content/text scale |
| Shapes/icons | Radii 8, 12, 16, 24 and proportional capsules; icon sizes 16, 20, 24, 32; ordinary border 1 dp |
| Typography | Inter: screenTitle 34/40 at 600; headline 28/34 at 600; sectionTitle 22/28 at 600; title 18/24 at 500; body 16/24, supporting 14/20 and caption 12/16 at 400; control labels 500 |
| Appearance | System/Light/Dark, reactive system observation, complete increased-contrast variants; no default dynamic recoloring |
| Motion | Press 100–150 ms; local changes 180–240 ms; appearance 250–350 ms; final curves and interactive choreography require recorded review |
| Width | Compact below 600 dp; medium 600–839 dp; expanded at least 840 dp; content and text scaling may force earlier reflow |

Pin identical font versions, optical-size selection and actual weight files across
platforms. Do not synthesize different weights. Qualify RTL fixture glyph coverage
and bundle a reviewed fallback if required; test fixtures do not expand release
language claims. Use shared Lucide vectors and preserve required notices.

Required colors include backgrounds and surface levels; primary/secondary/disabled/
inverse text; primary/secondary/disabled icons; accent and containers with paired
foregrounds; success/warning/error/info and content/container pairs; borders,
divider, selection, focus and scrim. Require ordinary text contrast at least 4.5:1
and qualifying large text 3:1 against actual composite backgrounds. White against
the brand primary must not be used as an unqualified normal-text action pair.
Record component-state/focus contrast separately from the bounded text-pair gate.

The complete palette table, per-role shadows, material parameters, reading widths,
and final motion values are explicit BDS-03/BDS-06 deliverables. They must have
recorded values, rationale and simulator evidence before their visual gates close;
provisional values cannot become qualified simply by being used in code.

## BUI-05: Component contract

Every C001–C092 export requires implementation, public API documentation, usage,
applicable states, accessibility semantics and behavioral evidence. The machine
catalog is authoritative for names and per-component obligations. Implementation
status belongs in the execution/evidence ledger, not inferred from this inventory.

Prefer slots, Modifier and caller-owned values or framework editing state.
State helpers may use `rememberApp...State`. Reuse Compose behavior when it meets
the contract. Keep vendor rendering types internal. Controls own no ViewModels,
OS prompts or navigation stacks. Loading suppresses duplicate activation and
exposes busy semantics. Selected, disabled, focused, invalid and read-only are
distinct applicable states, not one universal enum. Each essential gesture has
an accessible alternative. Rationale and API constraints belong in documentation
under the repository's handwritten-source convention.

## BUI-06: Navigation and saved state

One shared Navigation 3 owner holds independent tab stacks and stable entry IDs.
Features emit intents; design-system controls do not import routes. Preserve tab
history, scroll and in-memory edit buffers. Protect roots from empty-stack pops.
Back, Up, Close and Cancel have distinct meaning. Gesture progress is reversible;
cancel does not pop; completion commits once. Test arbitration with horizontal
content and sheet gestures. Entry work ends when the entry is removed.

Configure serializers explicitly for iOS. Restore only versioned, bounded,
allowlisted lightweight route IDs and suitable nonsecret saveable state. Corrupt,
unknown and incompatible payloads recover to a valid root. Apply the approved
persistence policy above; write preferences atomically using minimal host storage.
Validate fixture links and duplicate delivery, including unknown targets and
defined back paths. Production domains and OS associations are outside scope.

## BUI-07: Editing, asynchronous state and layout

Preserve selection, composing ranges, paste/delete, focus, IME submit, content
type and supported autofill. Secure values never enter restoration, logs or
captures. Labels and validation messages must be associated with their fields.
Dirty dismissal, cancel and save are workflow decisions. Suppress duplicate saves
and preserve draft state when dismissal is cancelled. Date-only values and instants
must remain distinct; calendar constraints, leap days and confirmation/cancellation
need tests against the selected date/time types.

Represent initial loading, usable content, retained-content refresh, empty, error,
offline and pagination separately. Cancel correctly, discard stale results and
provide deterministic retry behavior with injectable clocks/fakes. Use one owner
per system, keyboard and overlay inset. Test sheets, nested scroll, width changes,
large text and focus visibility without double padding or obscured actions.

## BUI-08: Glass

Backdrop is the initial internal adapter, subject to the compatibility prototype.
The reviewed foundation candidate is `io.github.kyant0:backdrop:2.0.0-alpha03`
under the existing compile SDK 36, Android API 28 and iOS 18 contracts. Retain this
pin through initial implementation unless a reviewed decision supersedes it.
Compatibility probes and later simulator/device gates still apply; selecting the
prerelease does not qualify physical performance or authorize a toolchain change.
An evidence-backed replacement requires a recorded specification decision.
`AppGlassHost` owns capture/policy; `AppGlassSurface` consumes a library-neutral
source. Full, Reduced and Opaque preserve semantics, hit testing, layout and actions.
Prefer opaque content/forms and selective glass navigation or floating controls.

Separate source capture and consumers; define draw order, coordinates, clipping,
scroll/inset transforms and lifetime. No self-capture, unbounded offscreen layers
or per-frame CPU framebuffer readback. Source loss falls back safely; background
and disposal stop unnecessary work. Native embedded surfaces need explicit support
evidence or fallback rather than an assumption of arbitrary refraction.

Preserve API 28. Resolve supported effects from a tested capability matrix, never
from the library's minimum SDK alone. Unknown/unavailable capability selects a
readable fallback. Accessibility preferences take precedence over decorative
effects; unavailable preference signals remain unknown. Provide deterministic
catalog overrides that cannot bypass capability/accessibility protections.

The compatibility catalog obtains capability from its host; a policy function
used only in tests does not qualify that path. Android below API 31 selects opaque
for this pinned probe. Deterministic fixtures may disable capability/effects but
must not force unsupported effects on. Assert readable rendered fallback and that
the unsupported effect is not created. BDS-02 uses both available simulator hosts
and injected unavailable capability; actual API 28 emulator execution is a separate
mandatory BDS-12 qualification case, not inferred from a Boolean test or a newer
emulator. Physical performance remains BDS-13.
Simulator profile/capture tests do not qualify physical performance.

## BUI-09: OS integration

Implement OS01–OS10 with lifecycle-safe, exactly-once requests, cancellation,
resource ownership and truthful platform-specific outcome guarantees. No blanket
permissions or prompts at startup, clipboard polling, assumed filesystem paths,
unbounded document reads, or delivery claims from share-sheet launch. Biometrics
do not establish an account identity. Haptics respect settings and may be a benign
unsupported no-op. Test supported simulator paths plus deterministic failure
fixtures; record hardware-only outcomes as not run until measured.

## BUI-10: Catalog and workflows

The catalog is a separate development consumer, excluded from production. Use
stable synthetic IDs, fixed ordering, deterministic media, controlled clocks and
bounded fake latency. The catalog and real diagnostic must both consume shared
modules without duplicating styling. A second-consumer smoke check proves reuse.

- FLOW-01: list/detail; switch tabs and return; retain scroll; cancel and complete
  back; change width and recreate supported host state.
- FLOW-02: open edit sheet; focus a low field with keyboard; compose/paste; reject
  invalid input; cancel dirty dismissal; save once and dismiss.
- FLOW-03: deterministic images with floating action/slider/toggle; picker cancel
  and selection; truthful share launch; profile changes; background/resume.

## BUI-11: Verification and completion

Use [existing commands](../development/commands.md) where applicable. Add new
repository-owned commands for uncovered gates and record actual task discovery;
do not claim a generic task executes Android and iOS merely by its name.

| Lane | Required evidence |
| --- | --- |
| V0 | JSON/contracts, requirement/component/service coverage, links, public API/scope review and diff hygiene |
| V1 | Native producer regression tests, environment/identity policy, Rust/native integrity and setup/build profiles |
| V2 | Shared/module tests and actual Android/iOS compilation; dependency/resource/API boundary checks |
| V3 | Android emulator and iOS simulator workflows, input/navigation/lifecycle/OS integration; nonzero executed test counts |
| V4 | Paired normalized captures, English/long/RTL fixtures, enlarged text, contrast, focus and available accessibility checks |
| V5 | Physical release builds: frame pacing, memory, input response, hardware services and accessibility, effects on/off |
| V6 | Standalone checkout, both consumers, locked dependency/resource delivery, existing Rust/host regression and CI evidence |

Every component has named tests, not only node-existence checks. Cover relevant
enabled/loading/selection/invalid/read-only/focus states, both appearances, contrast,
motion and effects profiles using risk-based combinations rather than a Cartesian
explosion. Pair equal content, logical frames, locale, scale, assets and profiles.
Mask only documented system regions. Seed geometry/color/font regressions to prove
the visual harness detects them. Derive and record tolerances from repeat captures;
do not relax them to conceal failures.

Qualification levels are source/build, simulator foundation, physical Android,
physical iOS and full foundation. BDS-12 may close as simulator-qualified with
BDS-13 explicitly outstanding. The ten adapter implementations must exist, but
device-only outcomes remain separately unqualified. Physical budgets and final
effects tuning require measured representative devices and recorded thresholds.
No simulator result can close V5. Device availability never blocks unrelated
simulator work. No signed store distribution is part of this gate.

Evidence records include scope, revision/candidate identity, commands, exit codes,
nonzero test counts, tool/OS/device/configuration, artifacts and limitations.
PASS requires execution; FAIL, PRE_EXISTING, NOT_RUN and BLOCKED remain distinct.
Store portable evidence indexes without credentials, personal device IDs or huge
raw bundles. New regressions block their slice; unrelated baseline failures need
bounded impact analysis rather than deletion or silent waiver.

## BUI-12: Execution and traceability

The final acceptance matrix has fifteen gates. Simulator qualification may close
only the simulator-supported portions; hardware portions remain attached to BDS-13.

| Gate | Acceptance obligation | Principal evidence |
| --- | --- | --- |
| AC-01 | Shared app-owned rendering and approved visual parity | Dependency audit and paired captures |
| AC-02 | Correct native input/back/lifecycle and OS interaction | Target integration plus physical checks |
| AC-03 | Internal replaceable glass and functional fallbacks | Capture/policy tests and device evidence |
| AC-04 | Reusable modules, thin hosts, catalog excluded | Dependency/API checks and second consumer |
| AC-05 | Reproducible complete tokens and shared resources | Alias/contrast/resource tests and notices |
| AC-06 | All 92 components implemented with applicable behavior | Complete component-to-evidence matrix |
| AC-07 | Navigation identity, back cancellation, links/restoration | Common and target navigation tests |
| AC-08 | Correct editing, validation and keyboard-aware forms | Editor tests and simulator/device flows |
| AC-09 | Explicit async states, retries and cancellation | Deterministic race/duplicate/stale-result tests |
| AC-10 | Accessible scalable/localizable presentation | English/RTL/contrast/focus/accessibility matrix |
| AC-11 | Adaptive state retention and correct insets | Window/keyboard/orientation tests |
| AC-12 | Three workflows and measured release effects behavior | Simulator workflows and physical performance |
| AC-13 | Existing runtime/identity/consumers preserved | Rust/native regression and compatibility review |
| AC-14 | Verified bounded execution and real checkpoints | RCLD ledger and owning command/revision receipts |
| AC-15 | Accurate contracts, usage and qualification reporting | Evidence index and unresolved hardware gates |

One RCLD owns each BDS unit. Its slices specify scope, dependencies, definition of
green and lanes. Keep only one implementation slice active in this sequence.
Verified uncommitted work is not a committed checkpoint. Record actual revisions
after they exist and preserve historical evidence rather than relabel it as fresh.
No source commits, pushes, deployments or external state changes follow merely
from a plan status. The repository-local issue database remains uninitialized;
these public execution documents own implementation progress until separately
adopted tracking supersedes that arrangement.

The component catalog, service catalog and BUI-01–BUI-12 requirements must map to
owning slices and evidence. No missing component, unrun device gate or unfinished
specification may disappear through a percentage-complete summary.
