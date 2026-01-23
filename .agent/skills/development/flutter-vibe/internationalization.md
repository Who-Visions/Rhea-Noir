# Internationalization (i18n)

Localize your app for different languages and regions using the `flutter_localizations` package and ARB files.

## 1. Setup

### pubspec.yaml
```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_localizations:
    sdk: flutter
  intl: any

flutter:
  generate: true // Enable code generation
```

### l10n.yaml (Project Root)
Configures the generation tool.
```yaml
arb-dir: lib/l10n
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
```

## 2. ARB Files (Translations)
Place in `lib/l10n/`.

**app_en.arb** (English - Template)
```json
{
  "helloWorld": "Hello World!",
  "@helloWorld": {
    "description": "The conventional newborn programmer greeting"
  },
  "greet": "Hello {name}",
  "@greet": {
    "placeholders": {
      "name": {
        "type": "String"
      }
    }
  },
  "wombats": "{count, plural, =0{No wombats} =1{1 wombat} other{{count} wombats}}"
}
```

**app_es.arb** (Spanish)
```json
{
  "helloWorld": "¡Hola Mundo!",
  "greet": "Hola {name}",
  "wombats": "{count, plural, =0{No wombats} =1{1 wombat} other{{count} wombats}}"
}
```

## 3. Usage

### Main Setup
```dart
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

MaterialApp(
  localizationsDelegates: [
    AppLocalizations.delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
  ],
  supportedLocales: [
    Locale('en'), // English
    Locale('es'), // Spanish
  ],
  home: MyHomePage(),
);
```

### In Widgets
```dart
Text(AppLocalizations.of(context)!.helloWorld);
Text(AppLocalizations.of(context)!.greet('Alice'));
Text(AppLocalizations.of(context)!.wombats(5));
```

## 4. Platform Specifics (iOS)
Update `ios/Runner/Info.plist` or project settings in Xcode to include supported locales (Localizations configuration) to ensure correct App Store listing.

## 5. Custom Date Formatting (`date_symbol_data_custom`)
Sometimes you need to load custom localizations or symbols for date formatting that aren't available by default.

### `initializeDateFormattingCustom`
This function allows you to load custom date formatting patterns and symbols for a specific locale.

```dart
import 'package:intl/date_symbol_data_custom.dart';
import 'package:intl/date_symbols.dart';

void main() {
  // Define custom symbols (simplified example)
  final customSymbols = DateSymbols(
    NAME: "CustomLocale",
    ERAS: ["BC", "AD"],
    ERANAMES: ["Before Christ", "Anno Domini"],
    NARROWMONTHS: ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"],
    STANDALONENARROWMONTHS: ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"],
    MONTHS: ["Jan", "Feb", ...],
    STANDALONEMONTHS: ["Jan", "Feb", ...],
    SHORTMONTHS: ["Jan", "Feb", ...],
    STANDALONESHORTMONTHS: ["Jan", "Feb", ...],
    WEEKDAYS: ["Sun", ...],
    STANDALONEWEEKDAYS: ["Sun", ...],
    SHORTWEEKDAYS: ["Sun", ...],
    STANDALONESHORTWEEKDAYS: ["Sun", ...],
    NARROWWEEKDAYS: ["S", ...],
    STANDALONENARROWWEEKDAYS: ["S", ...],
    SHORTQUARTERS: ["Q1", ...],
    QUARTERS: ["1st Quarter", ...],
    AMPMS: ["AM", "PM"],
    DATEFORMATS: ["yMd", ...],
    TIMEFORMATS: ["Hm", ...],
    AVAILABLEFORMATS: {"d": "d"},
    FIRSTDAYOFWEEK: 0,
    WEEKENDRANGE: [5, 6],
    FIRSTWEEKCUTOFFDAY: 0,
    DATETIMEFORMATS: ["{1} {0}", ...],
  );

  // Initialize for a custom locale ID
  initializeDateFormattingCustom(
    locale: "iso_8601",
    symbols: customSymbols,
    patterns: {"d": "d"},
  );
  
  // Now you can use this locale with DateFormat
  // final formatter = DateFormat('yyyy-MM-dd', 'iso_8601');
}
```

## 6. Dynamic Date Formatting (File & HTTP)

In scenarios where you need to load date formatting data dynamically (e.g., to support many locales without increasing bundle size, or to update formats without a new release), you can read symbols from the filesystem or a web server.

### File System (`date_symbol_data_file`)
Loads locale data from files. Useful for desktop or server-side Dart.

```dart
import 'package:intl/date_symbol_data_file.dart';

Future<void> setupLocale() async {
  // Initialize 'de' locale from a file path
  // The path must end with a directory separator
  await initializeDateFormatting('de', 'path/to/locale/data/');
}
```

### HTTP Request (`date_symbol_data_http_request`)
Loads locale data via HTTP. Useful for web apps or clients downloading on demand.

```dart
import 'package:intl/date_symbol_data_http_request.dart';

Future<void> setupLocale() async {
  // Initialize 'fr' locale from a URL
  // The URL must end with a slash
  await initializeDateFormatting('fr', 'https://example.com/locales/');
}
```


> [!NOTE]
> `availableLocalesForDateFormatting` provides a list of locales supported by these dynamic loading methods.

### Local Date Symbols (`date_symbol_data_local`)
Import this if you want to include ALL locale data in your app bundle (easier but increases size).

```dart
import 'package:intl/date_symbol_data_local.dart';

void main() {
  // Arguments are ignored as all data is available locally
  initializeDateFormatting(); 
}
```

## 7. Date Symbols Structure (`date_symbols`)
The `DateSymbols` class holds the low-level strings for formatting (month names, weekdays, first day of week).

- **`DateSymbols`**: The data container.
- **`en_USSymbols`**: Hard-coded constant for US English (always available).
- **`en_USPatterns`**: Date/time patterns for US English.

Usage is typically internal to `DateFormat`, but you can access it directly:
```dart
import 'package:intl/date_symbols.dart';


print(en_USSymbols.MONTHS); // [January, February, ...]
```

## 8. Date Time Patterns (`date_time_patterns`)
Defines the mapping from "skeletons" (e.g., "yMd") to locale-specific format strings.

- **`dateTimePatternMap()`**: Returns the globally available map of patterns.
- **Internal Use**: Typically managed by `DateFormat` when you pass a skeleton (e.g., `DateFormat.yMd()`).

```dart
// The skeleton "yMd" might map to:
// "M/d/y" in en_US
// "d.M.y" in de_DE
```

## 9. Finding System Locale (`find_locale`)

Sometimes you need to manually detect the system locale (e.g., in standalone Dart scripts or when Flutter's `DeviceLocale` resolution isn't sufficient).

### `findSystemLocale()`
Finds the system locale via native APIs and sets it as the default `Intl.systemLocale`.

```dart
import 'package:intl/intl_standalone.dart'; // Wraps findSystemLocale

  await findSystemLocale(); // e.g., returns "en_US"
  print(Intl.systemLocale); 
}
```


### Standalone Support (`intl_standalone`)
For native platforms (VM, Desktop, Server), use `intl_standalone` to access system locales.

```dart
import 'package:intl/intl_standalone.dart';

Future<void> main() async {
  await findSystemLocale(); // Checks OS settings
}
```

## 10. Locale Identifiers (`locale`)
Provides the standard `Locale` class implementation (Unicode Locale Identifier).

- **`Locale`**: Represents a language/region pair (e.g., `Locale.parse('en-US')`).
- **Parsing**: `Locale.parse('zh-Hant-TW')` handles complex tags.

## 11. Core Utilities (`package:intl`)
The `intl` package is the powerhouse behind formatting.

### Date & Number Support
- **`DateFormat`**: Locale-sensitive date formatting/parsing.
  - `DateFormat.yMd().format(DateTime.now())`
- **`NumberFormat`**: Locale-sensitive number formatting (currency, percent, decimal).
  - `NumberFormat.currency(locale: 'en_US', symbol: '$').format(123.45)`
- **`MicroMoney`**: Helper for storing currency as millionths (Int64) for precision.

### Bidirectional Text (`Bidi`)
Utilities for working with text containing mixed Local/Global directionalities (RTL vs LTR).
- **`Bidi.detectRtlDirectionality(text)`**: Returns true if text is RTL.
- **`BidiFormatter`**: Wraps text to enforce specific directionality.

### Utilities
- **`Intl`**: Entry point for messages and general locale setup.
- **`toBeginningOfSentenceCase(string)`**: Standardizes casing based on locale.

### Message Formatting (`message_format`)
Prepares strings for display with support for plurals and selects (ICU syntax).

- **`MessageFormat`**: Parses and formats messages.
  ```dart
  import 'package:intl/message_format.dart';

  var format = MessageFormat("Hello {name}, you have {count, plural, =0{no items} other{{count} items}}.");
  print(format.format({'name': 'Alice', 'count': 2})); 
  // "Hello Alice, you have 2 items."
  ```

## 12. Message Lookup (`message_lookup_by_library`)
The machinery behind localized message retrieval (used by generated code).

- **`MessageLookupByLibrary`**: Abstract base for generated message classes (e.g., `messages_en_US`).
- **`CompositeMessageLookup`**: Delegates lookups to specific library instances.

## 13. Number Symbols (`number_symbols`)
Low-level data for number formatting (decimal separators, infinity symbols, etc.).

- **`NumberSymbols`**: Holds symbols (decimal, grouping, zero digit).
- **`CompactNumberSymbols`**: Holds patterns for compact notation (e.g., "1.2M").

Usage is typically internal to `NumberFormat`, but accessible if needed for custom formatters.

### Data Access (`number_symbols_data`)
Global maps to access number formatting data by locale.

- **`numberFormatSymbols`**: `Map<String, NumberSymbols>` (Locale → Symbols).
- **`compactNumberSymbols`**: `Map<String, CompactNumberSymbols>` (Locale → Compact Patterns).
- **`currencyFractionDigits`**: `Map<String, int>` (Currency Code → Decimal Places).
