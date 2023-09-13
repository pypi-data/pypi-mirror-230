=======
History
=======

0.1.0 (2023-07-13)
------------------
* First release on PyPI.

0.2.0 (2023-07-26)
------------------
* Added function to retrieve defined indicams for user, in order to be able to test authentication without
  requiring a device definition to be entered at the authentication step.

0.3.0 (2023-07-26)
------------------
* Replaced the indicam listing function with an explicit connection test function.

0.3.1 (2023-08-25)
------------------
* Return "None" for measurement if error occurred or extraction failed at service.
* Made it so the client lives at indicam_client instead of indicam_client.indicam_client.

0.3.2 (2023-08-25)
------------------
* Fixed type in module include

0.3.3 (2023-08-25)
------------------
* Missed old-style module ref in tests
