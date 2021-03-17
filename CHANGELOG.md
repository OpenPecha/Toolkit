# Changelog

<!--next-version-placeholder-->

## v0.7.12 (2021-03-16)
### Fix
* Assets path ([`6a602b6`](https://github.com/OpenPecha/openpecha-toolkit/commit/6a602b62e647002aab780bb3142a5085b895b6f6))

## v0.7.11 (2021-03-16)
### Fix
* **epub-serializer:** Disabled font rescaling ([`1b63245`](https://github.com/OpenPecha/openpecha-toolkit/commit/1b6324512e751ad461c8a9d5a20783e505b208c0))
* **epub-serializer:** Margin given to sabche, citation and tsawa which are not inline ([`4cc8637`](https://github.com/OpenPecha/openpecha-toolkit/commit/4cc8637ba5abcf09c06ecf2a98040a86e23b5929))
* **epub-serializer:** Auto generation of TOC added ([`1db097c`](https://github.com/OpenPecha/openpecha-toolkit/commit/1db097c676a7be1514d0e694062713ec79d861de))
* **epub-serializer:** Footnote marker and reference serializer added ([`1446879`](https://github.com/OpenPecha/openpecha-toolkit/commit/14468792d780c38e5964a033261bc780a3099842))
* **epub-serializer:** Replace regular_indented1 of para before chapter title to regular_indented1 ([`fc243a6`](https://github.com/OpenPecha/openpecha-toolkit/commit/fc243a61bfa9eb225608710be9719ce53c3f170c))
* **tsadra-formatter:** Removed is_cover and is_subtitle. created new annotation sub title ([`7f0967a`](https://github.com/OpenPecha/openpecha-toolkit/commit/7f0967aace94d14bd4904fa45e853d619fdc015a))
* **epub-serializer:** Page break after chapter tag included ([`b481d59`](https://github.com/OpenPecha/openpecha-toolkit/commit/b481d59994f1aa04389db4e1d32999040f2a1dcd))
* **tsadra-formatter:** Yigchung formatter updated as corner case detected ([`870f198`](https://github.com/OpenPecha/openpecha-toolkit/commit/870f1980a1f695bae2cac081bf997621a94072da))
* **epub-serializer:** Intentation adjustment bug fix ([`018b5de`](https://github.com/OpenPecha/openpecha-toolkit/commit/018b5de92a75a24777d66fa6e53c423d4a1dad03))
* **epub-serializer:** Indentation bug fixed ([`ab405d5`](https://github.com/OpenPecha/openpecha-toolkit/commit/ab405d5456369d95b8488facf311cdb965d6d806))
* **epub-serializer:** Break within title bug are fixed by inserting break before title ([`fc3b8fa`](https://github.com/OpenPecha/openpecha-toolkit/commit/fc3b8fa995564ce64b8a94c7e8f41b2d2dcb75c6))
* **epub-serializer:** Indentation bug fixed for verse component ([`819c292`](https://github.com/OpenPecha/openpecha-toolkit/commit/819c292234c5c30c9e22fe866075f35a02703055))
* **tsadra-parser:** Credit page parser added ([`61c3648`](https://github.com/OpenPecha/openpecha-toolkit/commit/61c36480b2409278c3ba8a6a56906eebce3173b7))

## v0.7.10 (2021-03-11)
### Fix
* Add save_layer method ([`fd2b8a8`](https://github.com/OpenPecha/openpecha-toolkit/commit/fd2b8a8a1b7c7de9e26dea6f552830c9f2c06384))

## v0.7.9 (2021-03-11)
### Fix
* Remove 'opecha' from pecha id ([`064abab`](https://github.com/OpenPecha/openpecha-toolkit/commit/064ababcc64c823e7a849d250f2a8948dae187e1))

## v0.7.8 (2021-03-09)
### Fix
* Pecha has components list (base + layer names) ([`bb1d206`](https://github.com/OpenPecha/openpecha-toolkit/commit/bb1d206edba9e205184957255e875acea61b9e8f))

## v0.7.7 (2021-03-04)
### Fix
* Save pecha ([`9634fa9`](https://github.com/OpenPecha/openpecha-toolkit/commit/9634fa968215ff7cdb7cb12a95c561cc0ae51d4a))

## v0.7.6 (2021-03-03)
### Fix
* Iread pecha id from metadata ([`d9f008e`](https://github.com/OpenPecha/openpecha-toolkit/commit/d9f008ed52a66a0a3e4da0dd67d112a1625c5166))

## v0.7.5 (2021-03-03)
### Fix
*  blupdate test ([`2875e86`](https://github.com/OpenPecha/openpecha-toolkit/commit/2875e861b714e7d229609d75d6318af0b3f9abca))
*  download pecha with specific branch ([`4f4c9b7`](https://github.com/OpenPecha/openpecha-toolkit/commit/4f4c9b7c59452d6886c3eb5fccdb203d1cd55f25))
* Layer annotations are in dict ([`de625ff`](https://github.com/OpenPecha/openpecha-toolkit/commit/de625ff68efc17b5ddf122efb5662418bf2e2684))

## v0.7.4 (2021-03-02)


## v0.7.3 (2021-03-01)
### Fix
* Create review branch for opf ([`0bd7911`](https://github.com/OpenPecha/openpecha-toolkit/commit/0bd7911f0579cf9e766a74dace5bf223ac1df5dc))

## v0.7.2 (2021-03-01)
### Fix
* Ireturn empty string instead of None for source meta access ([`b2390f9`](https://github.com/OpenPecha/openpecha-toolkit/commit/b2390f9013853a327651255668adea0a2e55d98f))

## v0.7.1 (2021-03-01)
### Fix
* Make output_path optional ([`5b67259`](https://github.com/OpenPecha/openpecha-toolkit/commit/5b67259ece9c6434fd7a099f2e278dfeb83c5a53))

## v0.7.0 (2021-03-01)
### Feature
* Create empty ebook opf ([`cfb180d`](https://github.com/OpenPecha/openpecha-toolkit/commit/cfb180dfe92ec995d72ca8b7b6880291b5ac5795))

### Fix
* Cconfig for default pechas path ([`b92c3b7`](https://github.com/OpenPecha/openpecha-toolkit/commit/b92c3b7f5657ced29328d03333f226d4d421f166))

## v0.6.35 (2021-03-01)
### Fix
* Madd pydantic in dependencies ([`16f6ed0`](https://github.com/OpenPecha/openpecha-toolkit/commit/16f6ed0ed2dd613d5805598bc84ecbf4a96eda03))
* Add create opf for ebook ([`efe8bf8`](https://github.com/OpenPecha/openpecha-toolkit/commit/efe8bf8328b8d5c61c3cf221b0c1a6908c1ab2fe))

## v0.6.34 (2021-02-16)
### Fix
* Make methods to module funcs ([`7fec0d6`](https://github.com/OpenPecha/openpecha-toolkit/commit/7fec0d6af4a10efe4259e479641f5e5749911aa0))

## v0.6.33 (2021-02-09)
### Fix
* Csave src volumn id to base file in meta ([`50e2717`](https://github.com/OpenPecha/openpecha-toolkit/commit/50e271723ef148cfd092f1f5ddf35cdccb2b6bbd))

## v0.6.32 (2021-02-03)
### Fix
* Add needs_pecha option while pecha download ([`693086d`](https://github.com/OpenPecha/openpecha-toolkit/commit/693086d7aa5105d99fde68ccf8ce681066b46572))

## v0.6.31 (2021-01-21)
### Fix
* Test for old annotations structure ([`f8ea280`](https://github.com/OpenPecha/openpecha-toolkit/commit/f8ea2805881f7a903dbcc64de7bf2307b00e49ac))

## v0.6.30 (2021-01-21)
### Fix
* **git-utils:** Dpecha with main as default branch ([`9860836`](https://github.com/OpenPecha/openpecha-toolkit/commit/98608367df07f5b1552a02d5cab7833a911492a7))

## v0.6.29 (2021-01-20)
### Fix
* Missing encoding specification ([`051e2c2`](https://github.com/OpenPecha/openpecha-toolkit/commit/051e2c2e8bde4fe6e376be2ec6621770459a9c38))

## v0.6.28 (2021-01-19)
### Fix
* Update index layer ([`39f0422`](https://github.com/OpenPecha/openpecha-toolkit/commit/39f04228b6270a5d67c31dfa0aa918b6fa5395f1))

## v0.6.27 (2021-01-18)
### Fix
* Blupdate testcase and add cli ([`18d5a0c`](https://github.com/OpenPecha/openpecha-toolkit/commit/18d5a0c231608c80e4db904897c18b9314221fd2))

## v0.6.26 (2021-01-15)
### Fix
* **serializer:** Empty line serialize correctly ([`e906287`](https://github.com/OpenPecha/openpecha-toolkit/commit/e906287f36499accf356aa667f01dc84648194c0))
* Return local path of downloaded pecha ([`fae9e58`](https://github.com/OpenPecha/openpecha-toolkit/commit/fae9e58260bfdc73b3d7f37298012283fc26f079))
* **hfml-serializer:** Pagination needs to serialize last ([`468191b`](https://github.com/OpenPecha/openpecha-toolkit/commit/468191b536403c12c3775231b9fd90c11e5dbeac))
* **pagewise:** Pagewise obj created ([`2480e03`](https://github.com/OpenPecha/openpecha-toolkit/commit/2480e033c43b5129375cddc56f69025f3a8d70d1))
* **hfm-formatter:** Durchen parser added ([`a4bdd15`](https://github.com/OpenPecha/openpecha-toolkit/commit/a4bdd15f08f94be407811219e8f8d3e1f4d82eae))
* **serialize-base-module:** Empty line serialize correctly ([`cb4ebca`](https://github.com/OpenPecha/openpecha-toolkit/commit/cb4ebca1ad95871c2a441dd034ed68a1cb8775bd))
* **formatter-basemodule:** Pecha without text formatted correctly ([`ff5dee2`](https://github.com/OpenPecha/openpecha-toolkit/commit/ff5dee213eb7a29a7a58f5717f5f593bd321b073))
* **hmfl-formatter:** Empty line formatted correctly ([`5fcbe87`](https://github.com/OpenPecha/openpecha-toolkit/commit/5fcbe87a23260e28e95a1032e8c766d6f1cc790e))

<<<<<<< HEAD
## v0.6.23 (2021-01-15)
### Fix
* Return local path of downloaded pecha ([`fae9e58`](https://github.com/OpenPecha/openpecha-toolkit/commit/fae9e58260bfdc73b3d7f37298012283fc26f079))

## v0.6.22 (2021-01-12)
### Fix
* **hfml-serializer:** Pagination needs to serialize last ([`468191b`](https://github.com/OpenPecha/openpecha-toolkit/commit/468191b536403c12c3775231b9fd90c11e5dbeac))
* **pagewise:** Pagewise obj created ([`2480e03`](https://github.com/OpenPecha/openpecha-toolkit/commit/2480e033c43b5129375cddc56f69025f3a8d70d1))
* **hfm-formatter:** Durchen parser added ([`a4bdd15`](https://github.com/OpenPecha/openpecha-toolkit/commit/a4bdd15f08f94be407811219e8f8d3e1f4d82eae))
* **serialize-base-module:** Empty line serialize correctly ([`cb4ebca`](https://github.com/OpenPecha/openpecha-toolkit/commit/cb4ebca1ad95871c2a441dd034ed68a1cb8775bd))
* **formatter-basemodule:** Pecha without text formatted correctly ([`ff5dee2`](https://github.com/OpenPecha/openpecha-toolkit/commit/ff5dee213eb7a29a7a58f5717f5f593bd321b073))
* **hmfl-formatter:** Empty line formatted correctly ([`5fcbe87`](https://github.com/OpenPecha/openpecha-toolkit/commit/5fcbe87a23260e28e95a1032e8c766d6f1cc790e))

## v0.6.21 (2020-12-23)
### Fix
* Small bugs ([`a1b1016`](https://github.com/OpenPecha/openpecha-toolkit/commit/a1b1016d78caccfc0b86f82e477c8fd8b0954f8a))
=======
## v0.6.25 (2021-01-15)
### Fix
* Import bonltk only when in use ([`a7e5b48`](https://github.com/OpenPecha/openpecha-toolkit/commit/a7e5b487d65e2ba12440ecc1c9a28cfc5e650ce4))

## v0.6.24 (2021-01-15)
### Fix
* Import bonltk only when in use ([`3ecd475`](https://github.com/OpenPecha/openpecha-toolkit/commit/3ecd4751353191f0c37555ac5fbcf8897030039e))
* Return local path to downloaded pecha ([`e91fb4d`](https://github.com/OpenPecha/openpecha-toolkit/commit/e91fb4d5946c497c409dbef1ad26bfa5763097a4))
>>>>>>> bde09bb05942f5eb18923cf3326c2a5f7180a10f

## v0.6.20 (2020-11-23)
### Fix
* Break after 500 syllables ([`8d93203`](https://github.com/OpenPecha/openpecha-toolkit/commit/8d9320337029a232328dfcdf21ddb166a3f4f37e))

## v0.6.19 (2020-11-16)
### Fix
* Move catalog manager into catalog sub-pkg ([`fb6b084`](https://github.com/OpenPecha/openpecha-toolkit/commit/fb6b08442982c0a8aa0e49c862261ffed702d9b4))
* Download corpus cli ([`69b82e6`](https://github.com/OpenPecha/openpecha-toolkit/commit/69b82e61b926fa25cc71ecc151caed2c0b4f7eef))
* Get base of all pechas ([`878a31b`](https://github.com/OpenPecha/openpecha-toolkit/commit/878a31b87c3c4998ec30fce2c1db60443a26c737))

## v0.6.18 (2020-10-23)
### Fix
* Create_file to accept org and token ([`7bf1562`](https://github.com/OpenPecha/openpecha-toolkit/commit/7bf15622e57af244363e59d5c0f69e01ffb092a1))

## v0.6.17 (2020-10-23)
### Fix
* Github helper funcs to work on any org ([`b3aff03`](https://github.com/OpenPecha/openpecha-toolkit/commit/b3aff036bfbbd8bdcd69e3be1819575e5bfba8f2))

## v0.6.16 (2020-10-21)
### Fix
* Missing kwarg metadata ([`051ca1b`](https://github.com/OpenPecha/openpecha-toolkit/commit/051ca1bdcb795e2422bccf4fecd8355232f68e62))
* Create orphan branch for each layer ([`4ff76f7`](https://github.com/OpenPecha/openpecha-toolkit/commit/4ff76f768507ac242ce511e85414b8e0cabcebd2))
* Add source metadata ([`1b2bbe8`](https://github.com/OpenPecha/openpecha-toolkit/commit/1b2bbe8e7790555e9f73974977a095d37e626390))
* Add hfml item ([`81a982a`](https://github.com/OpenPecha/openpecha-toolkit/commit/81a982abc59283d8a7e95f999f8fb9ee6f33d53f))

## v0.6.15 (2020-10-15)
### Fix
* Disable line-number for epub ([`3ed677e`](https://github.com/OpenPecha/openpecha-toolkit/commit/3ed677ebb4ef221dbceb1aba4dc5db6a5fce26c6))

## v0.6.14 (2020-10-13)
### Fix
* Create prerelease and return asset download url ([`2b84ee3`](https://github.com/OpenPecha/openpecha-toolkit/commit/2b84ee39158e29b10a9a704dc42583966fbaa409))

## v0.6.13 (2020-10-08)
### Fix
* Return serialized epub path ([`7d3e8a9`](https://github.com/OpenPecha/openpecha-toolkit/commit/7d3e8a9700d498cb347dfc52ce1ab0572c74ffeb))

## v0.6.12 (2020-10-08)
### Fix
* Skip the hfml_serializer test for a new release ([`25fba24`](https://github.com/OpenPecha/openpecha-toolkit/commit/25fba241d4b1e94b08f2c96b300923dbe8009902))
* Unified opfpath to opf_path ([`9646b34`](https://github.com/OpenPecha/openpecha-toolkit/commit/9646b3450c73ab26736f3daf6ebb8ab104b61cdd))
* Pecha_id as arguments ([`e288b1d`](https://github.com/OpenPecha/openpecha-toolkit/commit/e288b1dc7524da4b1dad383775a791cbad14bd1b))
* Improve log message ([`338e661`](https://github.com/OpenPecha/openpecha-toolkit/commit/338e661581d30bb4bf427131cd21a2e70d9ab92d))
* Fix sub topic nested list ([`f22dcd1`](https://github.com/OpenPecha/openpecha-toolkit/commit/f22dcd1c54e2816e96ee2ba58a5a232c6abc7d10))
* Import error ([`218c2bf`](https://github.com/OpenPecha/openpecha-toolkit/commit/218c2bf6006ead18305a70b2db88fae4c37d6805))
