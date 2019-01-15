Change Log
==========

metar-1.7.0 (15 January 2019)
-----------------------------

This release is a bug fix and enhancement release with no known API breakages. The highlights include:

- [#77](https://github.com/python-metar/python-metar/issues/77) Support was added for I-group (ice accretion), see new `Metar` attributes `ice_accretion_1hr`, `ice_accretion_3hr`, and `ice_accretion_6hr`.
- [#70](https://github.com/python-metar/python-metar/issues/70) Code tests were migrated to pytest.
- [#64](https://github.com/python-metar/python-metar/issues/64) Cloud type `AC` is now supported.
- A number of pull requests were merged that improved the PEP8 and code style. The project's LICENSE was also clarifed as BSD.


metar-1.6.0 (20 August 2018)
----------------------------

The development of the `python-metar` library has been moved to a [Github Organization](https://github.com/python-metar) with the kind approval of Tom Pollard.  A few volunteers including @phobson and @akrherz look to maintain this library doing forward.  The best way to submit bug reports is through Github.

The 1.6.0 release is the first made by our new organization and signifies an effort to fix bugs and improve the API.  Here are some of the highlights with this release.

 - The `Metar` constructor now supports a `strict` parameter (see #51 and #36). When `strict=False`, the parsing of METARs will not raise exceptions for parsing failures nor unparsed groups.
 - Python 3.6 is formally supported and actively tested against.
 - `print` statements were replaced by standard library loggers.
 - In the case of a METAR that contains sea-level pressure (SLP) and not altimeter, the METAR object attribute `press` is left unset. (see #38)
 - METAR precipitation and snow reports can be of `Trace` value. (see #34)
 - It is now possible to override some class attributes (see #37)
 - Add support for METAR 4/ group (snow depth) (see #31)
 - Add method to show recent weather as string (see #21)
 - A few sundry code fixes, cleanups, and improvements to automated testing


metar-1.5 (18 December 2017)
---------------------------

Python-metar v1.5 includes updated documentation and a few minor bug fixes.
The old sourceforge site is no longer being updated, and so the only authoritative
source repository is the GitHub repo.  To clone the project from there, use

    git clone https://github.com/python-metar/python-metar.git



metar-1.4 (2 May 2009)
---------------------------
Python-metar v1.4 incorporates a handful of bug fixes and enhancements
made over the last couple of years.  Notably, Toby White contributed code to 
let the parser recognize and ignore trend forecasts and runway-state groups.

Starting with this release, new releases will be made available through my 
sourceforge project, at http://python-metar.sourceforge.net/.  I've also 
converted my code repository from CVS to Git, and made public copies of the 
Git repository available on Sourceforge and on Github. To clone the 
repository, you can use either

    git clone git://python-metar.git.sourceforge.net/gitroot/python-metar
or
    git clone git://github.com/tomp/python-metar.git


 - Merged Toby White's changes for parsing (and ignoring) runway state groups
   and trend forecasts. (Thanks!)

 - Report the peak wind and wind shift times, if included in the remarks.
   (Requested by Daryl Herzmann.)

 - Changed the date-handling code to avoid automatic month/year adjustment
   if the month or year are specified explicitly.  
   (Thanks to Scott McKuen for reporting this.)

 - Only allow single-digit numerator in fractional visibility values, to avoid
   confusion with following temp/dewpt group.
   (Reported by Franco Fiorese, Francesco Spada, and David Gregory.)

 - Fixed the misuse of str() function and string() methods in a couple of spots.
   (Reported by David Gregory and others.)

 - Added tests for the visibility, trend, and runway state parsers.

 - Added tests to verify that automatic month/year adjustment of the observation 
   date were being done correctly.

 - Updated links to METAR resources in the README


metar 1.3 (1 August 2006)
---------

 - The datatype classes now have __str__ methods, so you can user the 
   generic str() function to get their string representation.

 - 'MMM' is now accepted to represent missing data in the wind group.

 - Fixed bugs in the handling of wind observations reported in KMH and MPH.
   (Thanks to Erik Bryer for reporting the MPH problem.)

 - '/' placeholders for missing data in the weather group are handled better now.

 - Added tests for KMH and MPH conversions to the test_speed.py script.

 - Added tests for wind-group parsing to the test_metar.py script.

 - Accept "11/2" as equivalent to "1 1/2" in the visibility group.

 - Fixed a bug that prevented the error handler in get_report.py from reporting
   the error message :-)  (Thanks to Erik Bryer for reporting this.)


metar 1.2 (6 February 2005)
---------

 - Save the 1-, 3-, 6- and 24-hr preciptation values as Metar attributes.

 - Save the 6- and 24-hour max and min temperatures as Metar attributes.

 - Save the peak wind speed and direction as Metar attributes.

 - Save the sea-level pressure as a Metar attribute.  The sea-level
     pressure is treated as the station pressure, as well, if no station
     pressure is otherwise reported.

 - Added a peak_wind() method, to report peak wind data.

 - 'QNH' and 'SLP' pressure groups are now accepted.  'INS' at the end of
   a pressure group is recognized, as well.

 - A group of four digits is accepted as a pressure group, now.

 - Present-weather and cloud-cover lines are only written in the textual
   output if observations of those phenomena were reported.

 - The character 'O' is treated as a zero in the cloud-height, visibility
   and wind fields.

 - 'CORR' (in the modification field) is interpretted as 'COR'

 - 'NIL' and 'FINO' (in the modification field) are interpretted as 'NO DATA'

 - 'K', 'T' and 'LT' are all interpretted as 'KT'.

 - 'SCK' is interpretted as 'SKC'

 - 'MM' is now accepted as a placeholder in the 'temp' and 'dewpoint' groups.

 - An 'integrity' field ('+' or-) has been created.

 - 'RVRNO' groups are ignored, now.

 - '0VC' is treated as 'OVC'.

 -  A pressure group consisting of just four digits with no leading 'A' or
    'Q' is accepted now.  The units are assumed to be inches if the value
    is greater than 2500.

 - An 'O' in a cloud height field is treated as a '0'.

 - Modified to handle "MIFZFG".

 - Moved regexp matching out of the _parse* methods and into the `__init__`
   method.  This lets me avoid unnecessary method calls and removes a bunch
   of previously duplicated code.  It gives a 10-15% speedup.  The ability to 
   ignore trend groups has been temporarily lost as a result of this change.

 - The date parsing code will assume we're in the previous month if the day
   is greater than today's date.

 - Rearranged the VISIBILITY_RE regexp to fix a parsing bug,  which had
   caused "1 1/2SM" to be parsed as two groups.

 - Modified SKY_RE regexp to accept two to four digits in the cloud height,
   and to treat 'O' as '0', if found in the height.

 - Fixed a bug (a typo) in the vertical visibility handling code.  This was
   reported by Joseph Sheedy.

 - Fixed a bug in reporting maximum visibility when there was no direction
   for the maximum visibility.

 - Changed the way the visibility group was parsed to allow better
   handling of units.  '9999U' and '7000M' are now accepted.

 - Added support for sky group of the form '///030///', indicating cloud
   height without coverage or type info.

 - Support "KTS" as an alternative to "KT".
 - Support "XX" as a placeholder for a missing temperature or dewpoint.
(These are violations of the spec, but are sometimes used, anyway.)

metar 1.1 (28 January 2005)
---------

No notes available for this release.

metar 1.0 (16 August 2004)
---------

No notes available for this release.
