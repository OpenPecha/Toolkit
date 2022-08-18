# Changelog

<!--next-version-placeholder-->

## v0.8.26 (2022-08-18)
### Fix
* **buda:** Better API logging ([`74366e6`](https://github.com/OpenPecha/Toolkit/commit/74366e693c18980b681d6fe06d027ef58047c3f3))

## v0.8.25 (2022-08-18)
### Fix
* **googel-ocr-formatter:** Commit made to trigger githubaction to publish changes on pip ([`7f57883`](https://github.com/OpenPecha/Toolkit/commit/7f57883d84bc10351527a49ee6ce970ace404e50))

## v0.8.24 (2022-08-17)
### Fix
* **google-ocr-formatter:** Test case added ([`c8f2f1f`](https://github.com/OpenPecha/Toolkit/commit/c8f2f1fa003c1505707452631bfcf887b33d720b))
* **google-ocr-formatter:** Copy rigth variable updated ([`1e247bf`](https://github.com/OpenPecha/Toolkit/commit/1e247bfb0e9c61230401a67e8a711279026e0284))
* **google-ocr-formatter:** Code documated and test case updated ([`cb344d9`](https://github.com/OpenPecha/Toolkit/commit/cb344d9371eda2ee85ca633b079ce82cdf54aa6f))
* **googel-ocr-formatter:** Space insertion done using rule base algo ([`a5c596a`](https://github.com/OpenPecha/Toolkit/commit/a5c596a9ad9b1b7203e3e4aa9ec7c170b5b105fb))
* **setup:** Boto3 import added ([`0a39219`](https://github.com/OpenPecha/Toolkit/commit/0a39219290ce32bb3f5624ea2e3fe80fc0241725))
* **tmx-create-opf:** Base saving bug fixed ([`de88f86`](https://github.com/OpenPecha/Toolkit/commit/de88f8659c2380c72394aba8be2481db3ead9ebb))

## v0.8.23 (2022-08-17)
### Fix
* **core-pecha:** Find span info for all layers by default ([`973960a`](https://github.com/OpenPecha/Toolkit/commit/973960a06868c7ab16f4ef82611384cc1399f46e))
* **core-pecha:** Skip loading unsported layer ([`9e39086`](https://github.com/OpenPecha/Toolkit/commit/9e390868bc09e3342bafc6c6e9ae769d8ed6e48c))

## v0.8.22 (2022-08-12)
### Fix
* **google-ocr:** Add restrictedInchina, access, copyright, license to metadata ([`2055318`](https://github.com/OpenPecha/Toolkit/commit/2055318be4e77b033a586204e3fb8d9b49eec1f2))

## v0.8.21 (2022-08-11)
### Fix
* **metadata:** Add under copyright license ([`ceb9e39`](https://github.com/OpenPecha/Toolkit/commit/ceb9e39924c250fb9e0937c452ea0a174674e325))

## v0.8.20 (2022-08-10)
### Fix
* **google-ocr-formatter:** Meta title and author bug fixed ([`45b5b94`](https://github.com/OpenPecha/Toolkit/commit/45b5b942e7077ce6707f4f740de75787efbc1f05))
* **google-ocr-formatter:** Language layer formatter test case added ([`972278b`](https://github.com/OpenPecha/Toolkit/commit/972278bc0d0737826149614d74ded3e36c32204a))
* **google-ocr-formatter:** Language layer parser methods added ([`8f9ff0d`](https://github.com/OpenPecha/Toolkit/commit/8f9ff0da0cf8d84ec4bf65315021ba0ba633ab89))
* **google-ocr-formatter:** The ocr confidence index is saved in meta ([`b3ccd73`](https://github.com/OpenPecha/Toolkit/commit/b3ccd73e0d075dd7d1093f8abfd652a4947ff525))

### Documentation
* Add initial pecha metadata eg. ([`f0a07b6`](https://github.com/OpenPecha/Toolkit/commit/f0a07b6a61d0eaea3e94910a3b963a44ac7dcc52))

## v0.8.19 (2022-08-03)
### Fix
* **metadata:** Refactor initial metadata ([`125b0ab`](https://github.com/OpenPecha/Toolkit/commit/125b0ab118f9b77c9c289f4a91a582a9d2b43a60))

## v0.8.18 (2022-08-03)
### Fix
* **google-ocr:** Empty page bug fixed ([`9352526`](https://github.com/OpenPecha/Toolkit/commit/93525267fa6feaecfdf5db306f1511e1b587e07f))

### Documentation
* Add dependency ([`c861e95`](https://github.com/OpenPecha/Toolkit/commit/c861e95f2f6aa70af850e561cee29c0b861d23f5))
* Add pecha reference ([`9df1e5e`](https://github.com/OpenPecha/Toolkit/commit/9df1e5e9e6f6bc53d9d652b4622045ccf53000eb))

## v0.8.17 (2022-07-26)
### Fix
* Pypi release ([`31e4b47`](https://github.com/OpenPecha/Toolkit/commit/31e4b471eb0ec80f6989067ae90701604eb0abda))

### Documentation
* Add tab navigation ([`b8dad4a`](https://github.com/OpenPecha/Toolkit/commit/b8dad4aa1122a6243133f24dde59911cb1d0ecc2))
* **gh-action:** Add job to build and deploy docs ([`dc86ea6`](https://github.com/OpenPecha/Toolkit/commit/dc86ea6c3de5aeb491e017d7628c85fdffa5a33d))

## v0.8.16 (2022-07-22)
### Fix
* **config:** Github org url of openpecha data updated ([`61a7c2c`](https://github.com/OpenPecha/Openpecha-Toolkit/commit/61a7c2c8bfdc67e677541b61920628ab85770f5c))

## v0.8.15 (2022-07-22)
### Fix
* **blupdate:** Vol keywords are replaced by base name and related refactors are made ([`1eb61f3`](https://github.com/OpenPecha/Openpecha-Toolkit/commit/1eb61f368c8a58ddb454637337f3802ec8030183))

## v0.8.14 (2022-07-18)
### Fix
* **ocr-postprocessing:** The bounding polys are sorted before text extraction ([`3537a3f`](https://github.com/OpenPecha/Openpecha-Toolkit/commit/3537a3f76e26ea97eb1d29717172dce0fd255ed6))

## v0.8.13 (2022-06-13)
### Fix
* Set openpecha-data org name from env var only ([`e2e9052`](https://github.com/OpenPecha/openpecha-toolkit/commit/e2e9052827090b6e936f8d60dc3e28a2735ec4eb))

## v0.8.12 (2022-05-30)
### Fix
* **core:** Remove empty dict as default value in OpenPecha class ([`e863543`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e86354361807ca8dec6ed2be338c551cd378eeda))

## v0.8.11 (2022-05-25)
### Fix
* **metadata:** Add seperate metadata classes for pecha types ([`904f926`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/904f9264c2e895e1ff9f9e85abb15109f70177e7))
* **core:** Replace source id with initial id ([`ca083be`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/ca083be3f723ed3d9015b92e145c6830def16a3b))
* **core:** Add source and diplomatic id generator ([`24549dd`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/24549dd5c710caa506c022f999ab74a197564fed))

## v0.8.10 (2022-05-24)
### Fix
* **core:** Add copyright and license in metadata ([`1db55da`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1db55dad74631ee98b26d8d3127c598ec310c82e))
* **core-metadata:** Typos ([`d1b44f0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d1b44f03a88b2275b3122bb3505b52141f59c964))
* **core:** Move metadata model into metadata.py module ([`9f6f1a3`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/9f6f1a3c51a8b3f0b85f482393f36f4bf6d0b204))

### Documentation
* **metadata:** Add copyright and license to metadata ([`b15ab56`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b15ab56e5acdcb055887c5ad315a8bc5473d3f07))

## v0.8.9 (2022-05-24)
### Fix
* **serializer:** Apply index updated ([`be9a831`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/be9a8311939a5b9cdfc0947e35af3b5767cddcda))
* **serializer:** Vol id variables are renamed as base_id and vol keyword in span are changed to base ([`1d6898d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1d6898d9be7376963f865ec3da56547862a906c9))

## v0.8.8 (2022-05-18)
### Fix
* **corpus:** Create corpus directory ([`7ea0b5f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7ea0b5fc168d68b1a0e4e37ad0b8faeb0f3cd9e1))

## v0.8.7 (2022-05-18)
### Fix
* **core:** Remove prints ([`0cacb3d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0cacb3d267538150ece4161f05ee84ddfb62f3a0))
* **core:** Add metadata attr to OpenPecha class ([`8c5cb98`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8c5cb98ab0068ae0e95ece3826ecfd72b42c4e8d))
* **core:** Set base text metadata ([`5f34da2`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5f34da2851bb8693cc0015f58985d5e58fc42b83))

## v0.8.6 (2022-05-17)
### Fix
* **corpus:** Refactor to download tokenized corpus ([`b68bef0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b68bef00d0f7168484aded5f989032714d33526e))
* **corpus:** Lazy downloading corpus catalog csv file ([`cf24270`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/cf24270df4bbf993158cc2e0f17400138a5110e3))

## v0.8.5 (2022-05-12)
### Fix
* **corpus-quality:** Add statistics ([`6234b19`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/6234b19be946ef88fb361f290effc59b7e98698e))

## v0.8.4 (2022-05-11)
### Fix
* **core:** Pecha download ([`957c59d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/957c59dbf13b4b8101bff2968bd46c4255003787))

### Documentation
* Fix typos ([`ac04127`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/ac041275251b12bcd402ac93bce110769c15d635))

## v0.8.3 (2022-05-02)
### Fix
* **core:** Apply blupdate everytime base is upated ([`a899043`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a8990433c64d9591e34ecea235a5d7243adf3aed))
* **core-layer:** Update annotation ([`1553f41`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1553f414e52768c2e7a78e880ef12bd111b434b3))
* **core-annotation:** Add default and options spelling in durchen ([`e34c157`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e34c157faaf9e52ae866d87c25bec1d193f54ec7))

## v0.8.2 (2022-04-27)
### Fix
* **corpus-download:** Pecha base path ([`155feb0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/155feb0646b56073bf1967a1ff5fdee2fba3098d))

## v0.8.1 (2022-04-21)
### Fix
* **corpus-download:** Add download progress bar with tqdm ([`c075662`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c075662d55456ff8bd946aa59b72b79740099ce5))

## v0.8.0 (2022-04-01)
### Feature
* Create empty ebook opf ([`cfb180d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/cfb180dfe92ec995d72ca8b7b6880291b5ac5795))
* Add opf_path option for export command ([`facd1a9`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/facd1a9449bff01afe5b1de9140f14114bf9e685))
* Add assets to release ([`da7c279`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/da7c2792af8518f77ba1e2f36c0cd5065ffeacbd))
* Adapt annotations for shifted base-text ([`98251de`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/98251def9695f3149455f34804c436bae96764d4))
* Serializer of footnotes ([`3f0d21a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/3f0d21ac229fd600a9c545e42d9949170ffcfbcf))
* Use blupdate for fuzzy matching ([`877556c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/877556c3489e76ac20f36e7e6e05b99f667c2847))

### Fix
* **corpus-download:** Skip downloaded pecha" ([`f42e150`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f42e1500e3b714dc702c90d038fe465939552739))
* **corpus-download:** Use authenticated requests session ([`f0fe570`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f0fe5706591f452559c85a2e3d2f129ef50b278e))
* **corpus:** Get gh token for corpus download ([`94e3188`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/94e3188637c4cf7a53e0945105705463f8e03ceb))
* **download:** Download suggestion implemented ([`5dffcd6`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5dffcd646421ce04cafc427caf39b3541f7b8ef9))
* **download:** Base text url updated ([`db1d18b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/db1d18bd664fc85ce5aab146de4f696b78dcaf1a))
* **doc:** Documented download function in corpus module ([`f381a3f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f381a3facf70596e82d6319c292dffa1b4a9c8f7))
* **corpus:** Download corpus module compeleted ([`8b9cc73`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8b9cc73849015cfeaaa13336d3b2af881f677d4f))
* Add missing __init__ ([`3adacbc`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/3adacbce184bff0ed41f3b723ac5737aa328a7e9))
* **cli:** Transifex imports in cli ([`de530cf`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/de530cf23fc2438223e9fc12e33e9d362fef868b))
* Typos in cli ([`c8b9183`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c8b91838ce678e9cf3e658c8c77ce27d30961cf7))
* Missing __init__ file ([`b1ddca8`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b1ddca841054de8e226f09331dacaab4aec313fd))
* OpenPechaFS path ([`b99a041`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b99a04114a91310685759c416447d5723427219c))
* Add cli to count non word and save in meta.yml ([`5ac97c5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5ac97c58ac148e49415436f92ad0387cfb8722ca))
* Twn non_word conter can be added ([`8825625`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8825625c2ad4ef1ff9be25c11aaf72180fa0e152))
* **core-pecha:** Add pecha text quality attr in meta ([`e0a59cf`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e0a59cfb976df3cc33729861f255aa3bad24e4ce))
* **core-pecha:** Retrive span info ([`0fb51b9`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0fb51b9b59afd35566d32199f8c2f0ee8577673b))
* **core-pecha:** Add update last modified date ([`6285f79`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/6285f7962ed32e7e07c38a4d82881298303d6295))
* **core:** Remove layer_name arg from set_layer ([`e88fe77`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e88fe777ccf6bfa5f2d6267f385376134bd9c3fb))
* **core:** Set base and layer with OpenPecha ([`bb2f6d4`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/bb2f6d469bcf18a6b9c014165c183a0bab0c1006))
* **core:** Layer can add, get and remove annotation from it ([`eed2086`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/eed20864b6f0ff8693d32b4125fa8cbd12cdbae1))
* Pydantic version ([`525d980`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/525d980de76622c7e59964ad56742e22593033d4))
* **core:** Add remaining annotaion classes ([`e12b4e0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e12b4e02ab59fb5428cd92541e7e2375c32240fb))
* **core:** Forbid extra parameter in Annotation init ([`1d0ccb0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1d0ccb02922f5bc1f3d2f4736ca63cb9dbfea3b6))
* **core:** Add Citation annotation ([`bd1538d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/bd1538d0dbb7292a538f42152a8d7e09eb90d649))
* **storage:** Set remote url ([`23d4570`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/23d4570fd996f61836b8db4e61fb4d6d7599b479))
* **github:** Remove return in update pecha download ([`de1c237`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/de1c237b222029fa271eef98c3a66da14515f8e0))
* **github:** Setup repo auth when download ([`cf315b4`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/cf315b4f77e2e02b0009a15b20653e4b58ae04a5))
* **github:** Setup auth for download repo ([`a11c86e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a11c86e9617aeb2a5d71f09e16cbf7dae259df8c))
* **storages:** Add github repo auth ([`5b8cf8e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5b8cf8e21c5d12ef28d7e23603b4345faebfbafc))
* **core:** Set default output path to save work ([`9488419`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/9488419a31c4bc046959940f238e87a3e69907c2))
* **core:** Rset deefault path to save work ([`0b11e67`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0b11e67edd047b3a0c3057d4e8b1af3831e6f03b))
* **work:** Opwork id can be searched using bdrc instance id ([`a97796d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a97796d550d8b7515cbdb31b8cae614204e0d62f))
* **work:** Aadd load work from id ([`d75d67b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d75d67b238d00bdde8f3d4f3bb54ad60fdf44e97))
* **core:** Move work in work sub-pkg ([`691f9ee`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/691f9ee4324dfc91d05fd440a91183ce56ab9e73))
* **core:** Save and load workk from yaml ([`1fba453`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1fba453b9312957cebc33ae896d9dff483d9fc54))
* **core:** Add Work model and test ([`366540d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/366540dab431ac5de303802e617539ff20bf34db))
* **core:** Get id for pecha, work, alignment and collection ([`aa88541`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/aa88541272ab4897f2ff957af1fe1e46c4a4fe55))
* **work:** Add work test ([`caf8b52`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/caf8b52bc1b5a46114e9dfbc6f1a410201334f28))
* **github-storage:** Rename publisher to storage and add and remove file ([`557f5d8`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/557f5d80ff2406cfa506d1b5ff5a3e8292888b88))
* **publisher-github:** Remove and get repo ([`550c486`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/550c48643d794eaf5cc076112d28a78bb91a3a25))
* **publishers-github:** Aget dpecha description from about prop ([`93a341a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/93a341a0b11215dae38a1466edf66af0bedf82b3))
* **publishers-github:** Cimake path optional when remove pecha ([`6c004f0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/6c004f069c175b7d40b6b4071b28c1ae4ee55cec))
* **core-publisher:** Add base publisher class ([`7746060`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/774606092305123223b887b4534174b733a8f03a))
* **hfml:** Page annotation updated ([`a7eec5e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a7eec5e12ddce18d0ed1dbb732a42cf48f94dd09))
* **alignment-transifex:** Set transifex project repo url ([`26bae15`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/26bae15fe01466aae0498231242b2628f3a9e0d1))
* **alignment-tmx:** Add relation to alignment.yml's segmentsource ([`1a00972`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1a00972e0b171774c09700c39522dacf819308ea))
* **alignment-tmx:** Add relation to alignment.yml's segmentsource ([`db65e41`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/db65e41cd2edf4d00de320b2eefb58374eec32db))
* **alignment-tmx:** Add relation to alignment.yml's segmentsource ([`b96adc3`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b96adc3923ba700ffd132c6cb66da9a2bf6ceb51))
* **po:** Po view look up done on relation ([`1d81623`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1d816239cc95dfe65a4833d2dad36f7fbcf08724))
* **alignment:** Add import alignment cli ([`dc8aff0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/dc8aff09f5e0533cd4ba4e9b35eca0584c458a23))
* **alignment:** Return alignment repo path ([`7d0bf1c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7d0bf1cce3ad813a5c6734dc8366033f9730b8da))
* **alignment:** Default branch is master ([`413acbe`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/413acbe47b1f28696044bb5d04a1ccd371721e6c))
* **alignment:** Return project id and alignment title ([`c54b82d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c54b82d805d67b6368f18cd9e6d43fa2a01df405))
* **alignment:** Base in exporter ([`4ce9e99`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/4ce9e99d2520d6af66a1a457d7f3185d8b0a89ce))
* **alignment:** Load metadata ([`876b817`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/876b817c952d5061f6b30839a7b111640fb170c7))
* **alignment-tmx:** Add tmx parsers and po parsers ([`e462628`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e4626286024eff5220803b5cd4a854147b2015cb))
* **alignment-tmx:** Add tmx parsers and po parsers ([`cb7703c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/cb7703c56539b7074a02a85b9f934ef1cdce0272))
* **test:** Test data included separately ([`e951fca`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e951fca4e36d7ef17d2dd62e0103375ee77d1879))
* **blupdate:**  typos in update span ([`8d089f5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8d089f51f58d2a0a59afa252df36fedc6a9361be))
* **test:** Po test data separated ([`3a92be9`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/3a92be9bc03127e07e0e7a56bf1e7b893b6c509c))
* **test:** Po test data separated ([`461e0f1`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/461e0f10aa07ba3d81939e7c515816a6b18dbfcc))
* **po:** Language added while po export ([`8fcb59c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8fcb59cfd08f45b560bce6faac204c918003987c))
* **alignment-tmx:** Add create alignment from tmx ([`049d970`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/049d9708484de52ccf0548d7f560258d337a05ef))
* **po:** Po exporter updated ([`e25d1db`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e25d1dbd347ca315b4e1373d07f4b5c986f9e53e))
* **alignment-tmx:** Add create alignment from tmx ([`ed3588c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/ed3588cf536a4c320aaacf9512f2652560a108a1))
* **alignment-tmx:** Add create alignment from tmx ([`8c2c592`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8c2c592fd28d78377fd2876fa1a078e2b7f608ff))
* **alignment:** Get po view added ([`b832737`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b8327379e876dd94bb0a4c5df7aed026c16c3552))
* **po:** Keyerro bug fixed and functions documented ([`d7ead02`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d7ead026f0f8a4c87b11347a5493481d079fc290))
* **test:** Test code updated ([`dbbae52`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/dbbae523a692e541f39d7ab9105457ab982d4a61))
* **alignment-transifex:** Add traget language to the project ([`8a89e01`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8a89e017b7058862039382cc9ddd04184681b151))
* **po:** Po view populated to po branch ([`226d36b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/226d36b91c4179286f898dc0d6a2fa8844b1e37c))
* **bitext:** Bitext exporter implemented ([`538c3e7`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/538c3e7a8ce38ad8d60d80940225d1286f359a6e))
* **alignment-transifex:** Add TM to transifex project ([`7d861f0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7d861f0d27407f9bb10ad04512c0c3837f915e2f))
* **po:** Po exporter implemented ([`26bd01d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/26bd01d34ca6770b96919ca35d3e19cf5863177e))
* **google-ocr:** Flag added if meta required or not ([`1a80bc2`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1a80bc29343a44df9c46b541a4b4351797b49c9e))
* **google-ocr:** Post processing for page is done to google ocred pages ([`62db212`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/62db212b002b41acdf1f4fde134e7a2abc4373c3))
* **save_page:** Starting of text in same vol updated properly ([`eb273e0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/eb273e0d4db114ee778882ecb7a0cfbbb917dde5))
* **proofreading:** Span of sub text is update bug fixed ([`434638d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/434638db2d9f28408cb68bdac4b751a9b03525d0))
* **docx-serializer:** Font family included in styles ([`f794ca5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f794ca5ad23483ae92ca0ce15fb2ead1ba990be8))
* **serialisers:** Unify aserialize api ([`3faa1b5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/3faa1b51eb3aad2475ec846d4457551590364fbc))
* **editor-serializer:** Multiple tsawa and citation type supported ([`d65835d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d65835dfdcb20d8bdd8a50f2dbe7ea448ac1076c))
* **epub:** Enum used to avoid hardcoded condition checking ([`306a9c0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/306a9c0dbe7e42787fe3481ec3af7f88a9d2714e))
* **editor-formatter:** Ann type supports ([`b8a5f5a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b8a5f5ab330ed5918f98008933b9147e797c3d3a))
* **proofreading:** Subtext start update bug fixed ([`0fbeb4d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0fbeb4d668d222f049a31b768200d48b34d3f594))
* **docx-serializer:** Docx serializer formatted as class ([`024f19a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/024f19aa890d26f34cbeb8da3c4fa7503f901dfa))
* **test:** Pecha asset added ([`f97fa31`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f97fa3140e3c1d35fcbddd528c951fa8c7e0246a))
* **test:** Chapter and booknumber added ([`8d3a56c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8d3a56c3039bfcfb1c025d4cf1a9ea9575f9a32a))
* **testcase:** New test case added ([`fff431f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/fff431f09dbfc09d2d08fe4ce410d8b824ebfffb))
* **epub-serializer:** Multiple type of citation and tsawa annotation supported ([`c35d7cf`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c35d7cf2f5302d75e43a306e9ff3121a01008c55))
* **testcase:** Test case imporved ([`97d3b4b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/97d3b4bba62167afa87f3aa5b7d2520acbfc933d))
* **hfml-serializer:** Subtext serializer bug fix ([`01d31c2`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/01d31c2d7fd7952e80bde77d27c35c67c0fa309a))
* **proofreading:** Branch bug fixed ([`5702684`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5702684a0ffa35d7210c64db3105833769d711f2))
* **cli:** Also check for remote branch ([`224e170`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/224e170d087debb377645b8be04bd343ef97d652))
* **cli:** Pass repo in branch evaluate ([`f3feebd`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f3feebd6691b1c1df9eb3fe29dc3ffc25f57bf05))
* **proofreading:** Branch option and sub text update included ([`af04c6f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/af04c6f29a0cff16353118a62a25b065af94a446))
* **download-pecha:** Set fallback branch ([`0286d53`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0286d53a803a2afa45b44907a7da0b6c235a6351))
* **proofreading:** Vol info return list of volume details ([`b8164a6`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b8164a669c24ce014f51d6ae7feb00d5cc47c8b9))
* **proofreading:** Method to assist proof reading editor added ([`d874f91`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d874f9170e59252607194812d27cfea072d63971))
* **epub-test:** Test case updated according to new book title tag ([`d2c0d7f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d2c0d7fdbc017d031a4166673cb61034b44e0ee1))
* **docx:** Test added to docx serializer ([`97c1c87`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/97c1c8780f9f74655ab987030561141718d03fe5))
* **test-formatter:** Pedurma testcase updated according to changes made in formatter ([`8de3f01`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8de3f01fcb9f5f0e7f9a236186336624f019ff31))
* **hfml:** Self.dump replace to dump_yaml from utils ([`b96eb87`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b96eb87a158074ab245e7569fcdceae9575f4291))
* Pagination layer name typo ([`29b6ede`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/29b6edee2b7ddcf06a1fb996175a41ad004e672b))
* **docx:** Docx serializer added ([`c26b0cd`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c26b0cd9766245c45757d696e8ec96ef75706c74))
* **pedurma:** Formatter and serializer test case updated ([`d965422`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d96542236a1b8db7ce04d3e8ead55608073aa8b9))
* **utils:** Yaml loader and dumper is changed to Csafeloader and Csafedumper ([`da8ff8b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/da8ff8b386055357be71db25a7d7f422b554dbdd))
* **pedurma-formatter:** Pagination annotation changed to hfml format ([`bb80bbd`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/bb80bbd276cc1d0cf72a167c85bffab62838cefb))
* Raise exception for pecha doesn't exist ([`69aa954`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/69aa954f3970b1e2cfd8e740e24d308ec86c9154))
* **pedurma-serializer:** Doc string added ([`b9613ae`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b9613aee8dc51a25a91b18bb6a4461e8267492c8))
* **test:** Merge conflict resolved ([`9bb1a6c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/9bb1a6cf97cb350fd9711ea989ffd900a9552af1))
* **test:** Test case added for pedurma formatter and serializer ([`64d2b98`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/64d2b988b95ba1107c9ea3c3a5c83814a05abf20))
* **pedumra:** Formatter for preview text and serializer of diplomatic text completed ([`d7ee2f5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d7ee2f5f34c0967080365a7e2316329ab69b835b))
* **core-pecha:** Reset layers by reading components ([`031b8bb`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/031b8bb037c4fceb65b4010a212ed0c220ad303c))
* **core.pecha:** Add rest layers ([`7d25a4a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7d25a4a36f47c98a2520d1b9c71bddf7a1cbc12a))
* **pedurma-formatter:** Integration completed ([`5691391`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5691391c86c1d38fd5dc95a4a4936a9fa6b23185))
* **test:** Test for serializers are separated ([`0ed687a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0ed687a0d8295de89144c68b173460370bdbbc69))
* **editor:** Chapter serialize correctly in editor ([`cd2572a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/cd2572ab7f73e61ddabb00d70f32f6d5d6c8c170))
* **pedurmaFormatter:** Pedurma note formatter and serializer added ([`c39863b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c39863bf0bb6efd16dc140d9622c0a1ad93897ef))
* **serialize:** Text span bug fix ([`29ae052`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/29ae052deb27b14d707f266367ad9b5b3b4434e5))
* **hfml-formatter:** Topic end span for last page changed ([`a1d36de`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a1d36de32e8c426ef78421379e5825c82f0f18db))
* **serializer:** Line annotation removed ([`e3af107`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e3af107c777b8967260a14723a37cf4ee36dfafa))
* **epub-serialise:** Skip embedding ibook specification if epub doesnt exist ([`07b4acc`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/07b4acc747556fb39b7eb37cc6a05c817cf048e3))
* **epub-serializer:** Renaming approch changed ([`ec620f4`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/ec620f4e53f48a22a2dc749ace4396c39becaf44))
* **test-serialize:** Epub serializer updated ([`d117d86`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d117d867d87dc3771412d442a6463370ba7380c2))
* **epub-serializer:** Ibook specification for proper font embedding included ([`107cb69`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/107cb691e03ef9a93c08e4ed5c13dc2279cb24ac))
* **text-formatter:** Text-formatter added ([`b78698f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b78698fa71487bc44f01c8468010717626a140b0))
* **hfml-serializer:** Page index changed to imgnum ([`d83a86d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d83a86de12a0bdb6325a9a6ae4ce5ba9531c0706))
* New release ([`e16260c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e16260c6f9c024ab78661c3810581e33a1297254))
* **epub-serializer:** Alt option added for img tag of credit page ([`540c6fa`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/540c6faf86745ae0e1f369126a74b616feff815c))
* **serializer:** Index layer passed as parameter in order to avoid multiple loading of it ([`61a53ae`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/61a53aed4721e03421dd26eb46c2d06898843b9a))
* **epub-serializer:** Verse type annotation style changed ([`788ecab`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/788ecab70cd108fc65dc64da8fd9774e24568f6f))
* **hfml-serializer:** Extra line at the end of pages bug resolved ([`395ec95`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/395ec95ab0f29be7b665654ffc2187c873e2bf89))
* Ann start ([`aa0cc38`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/aa0cc389507037590e654e99bf31240109bbfba0))
* Ncreate  single ann as a group ([`b78bcf0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b78bcf0c53b9e5b2c34d436688f0d950c616c7d2))
* Specify upper and lower bound for deps ([`cb2a629`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/cb2a629c86b954d990b1a063b4c4d86d1ec7fa08))
* **epub-serialize:** Added front page generator using meta data ([`6f48523`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/6f48523feb34686229f2ebbff2f58e21126fc2e0))
* **editor-formatter:** Skip grouping if layer is empty ([`bd651cd`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/bd651cd04cd51540a81f484db2663d6a36606cc9))
* Exlude alll ann attrs with value none ([`c2408e4`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c2408e4e6f9ff7b1bb15dfa448006fe4773d97ea))
* **google-ocr:** Add imgnum to page ann ([`76ccc8d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/76ccc8dbb7f08fd67bea1c6ad16459d96e64bd50))
* **epub:** Set default toc level if exist in serialized html ([`d475e15`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d475e15f4cd0daa0ead7e3ff049f2ea92c2d6c03))
* Create layer if doesn't exist ([`af3ab83`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/af3ab83833f36198308389184ac368d84b9fcffc))
* **verse-annotation:** Isverse attribute of verse type annotation changed to is_verse ([`4173c1a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/4173c1a66d9c3f68dbc7a38fdb6e1c3b56d99d69))
* **test_serializer:** Testcase added for editor serializer ([`2c4d653`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/2c4d653c0e61e4830d997de449cc7742092badbc))
* **editor-serializer:** P tag introduced to verse components ([`7d4800f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7d4800f9674cd7d18bbae089085f783248e63253))
* Grouping root-text and find verse ([`a1a2484`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a1a248452f29b5dc38fbfb6614bc7149e0c859d2))
* Editor parser span ([`9242571`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/9242571a9f86f1f8860ac3e3367cf052be1a298f))
* Radd missing layers and improve test ([`f336aef`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f336aef99808242a1a69bd9c61abb6940c2b4bb1))
* Return output from editor serializer instead of saving ([`c6297c0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c6297c056203e932af31edf915ef33a0f1357321))
* **editor-serializer:** Footnote serialization enabled ([`53149e3`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/53149e37c2fbc76c00f7baad787e7afd6abdee53))
* Author css class ([`583d688`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/583d6885a1714fdc9c3fa2c71978149b4070f9ee))
* **editor-serializer:** Added special serializer for editor ([`0de0dbf`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0de0dbf4667e78e3e3d39f70cbcf51f21d51c00a))
* Aupdate base and layers ([`96c95b8`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/96c95b8c3db9d002121806b957a20380b8bba155))
* Add editor outpur parser ([`ef85a5f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/ef85a5f1e8bebe19ec0cf6eb05ef394f2f783dd2))
* **epub-serializer:** Removed credit page layer n added credit page img tag after first author ([`0342a17`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0342a179862aa663fe38059290bf67332bb3f1e8))
* **epub-serializer:** Removed credit page layer n added credit page img tag after first author ([`044e119`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/044e119ecdc8638b243128e15788d51307636f19))
* Cbranch checkout in pecha download ([`d89c607`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d89c607f5d78d92975833b1ec9bb92cefe99da7b))
* Toc level variable changed ([`c5c07af`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c5c07af6d5425c7c2640a2102874c22ad4b1a1e5))
* Toc level variable changed ([`3734339`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/3734339fee49d463211f0ca67dfb316d3f30181d))
* Assets path ([`6a602b6`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/6a602b62e647002aab780bb3142a5085b895b6f6))
* **epub-serializer:** Disabled font rescaling ([`1b63245`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1b6324512e751ad461c8a9d5a20783e505b208c0))
* Add save_layer method ([`fd2b8a8`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/fd2b8a8a1b7c7de9e26dea6f552830c9f2c06384))
* Remove 'opecha' from pecha id ([`064abab`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/064ababcc64c823e7a849d250f2a8948dae187e1))
* **epub-serializer:** Margin given to sabche, citation and tsawa which are not inline ([`4cc8637`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/4cc8637ba5abcf09c06ecf2a98040a86e23b5929))
* Pecha has components list (base + layer names) ([`bb1d206`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/bb1d206edba9e205184957255e875acea61b9e8f))
* **epub-serializer:** Auto generation of TOC added ([`1db097c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1db097c676a7be1514d0e694062713ec79d861de))
* **epub-serializer:** Footnote marker and reference serializer added ([`1446879`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/14468792d780c38e5964a033261bc780a3099842))
* Save pecha ([`9634fa9`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/9634fa968215ff7cdb7cb12a95c561cc0ae51d4a))
* Iread pecha id from metadata ([`d9f008e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d9f008ed52a66a0a3e4da0dd67d112a1625c5166))
*  blupdate test ([`2875e86`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/2875e861b714e7d229609d75d6318af0b3f9abca))
*  download pecha with specific branch ([`4f4c9b7`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/4f4c9b7c59452d6886c3eb5fccdb203d1cd55f25))
* **epub-serializer:** Replace regular_indented1 of para before chapter title to regular_indented1 ([`fc243a6`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/fc243a61bfa9eb225608710be9719ce53c3f170c))
* **tsadra-formatter:** Removed is_cover and is_subtitle. created new annotation sub title ([`7f0967a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7f0967aace94d14bd4904fa45e853d619fdc015a))
* Layer annotations are in dict ([`de625ff`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/de625ff68efc17b5ddf122efb5662418bf2e2684))
* Re-relase the 0.7.3 ([`337b3cc`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/337b3ccfefc9e624a076bcb7eca5ab38339128b2))
* Create review branch for opf ([`0bd7911`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0bd7911f0579cf9e766a74dace5bf223ac1df5dc))
* Ireturn empty string instead of None for source meta access ([`b2390f9`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b2390f9013853a327651255668adea0a2e55d98f))
* Make output_path optional ([`5b67259`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5b67259ece9c6434fd7a099f2e278dfeb83c5a53))
* **epub-serializer:** Page break after chapter tag included ([`b481d59`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b481d59994f1aa04389db4e1d32999040f2a1dcd))
* Cconfig for default pechas path ([`b92c3b7`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b92c3b7f5657ced29328d03333f226d4d421f166))
* Madd pydantic in dependencies ([`16f6ed0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/16f6ed0ed2dd613d5805598bc84ecbf4a96eda03))
* Add create opf for ebook ([`efe8bf8`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/efe8bf8328b8d5c61c3cf221b0c1a6908c1ab2fe))
* **tsadra-formatter:** Yigchung formatter updated as corner case detected ([`870f198`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/870f1980a1f695bae2cac081bf997621a94072da))
* **epub-serializer:** Intentation adjustment bug fix ([`018b5de`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/018b5de92a75a24777d66fa6e53c423d4a1dad03))
* **epub-serializer:** Indentation bug fixed ([`ab405d5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/ab405d5456369d95b8488facf311cdb965d6d806))
* **epub-serializer:** Break within title bug are fixed by inserting break before title ([`fc3b8fa`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/fc3b8fa995564ce64b8a94c7e8f41b2d2dcb75c6))
* **epub-serializer:** Indentation bug fixed for verse component ([`819c292`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/819c292234c5c30c9e22fe866075f35a02703055))
* **tsadra-parser:** Credit page parser added ([`61c3648`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/61c36480b2409278c3ba8a6a56906eebce3173b7))
* Make methods to module funcs ([`7fec0d6`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7fec0d6af4a10efe4259e479641f5e5749911aa0))
* Csave src volumn id to base file in meta ([`50e2717`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/50e271723ef148cfd092f1f5ddf35cdccb2b6bbd))
* Add needs_pecha option while pecha download ([`693086d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/693086d7aa5105d99fde68ccf8ce681066b46572))
* Test for old annotations structure ([`f8ea280`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f8ea2805881f7a903dbcc64de7bf2307b00e49ac))
* **git-utils:** Dpecha with main as default branch ([`9860836`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/98608367df07f5b1552a02d5cab7833a911492a7))
* Missing encoding specification ([`051e2c2`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/051e2c2e8bde4fe6e376be2ec6621770459a9c38))
* Update index layer ([`39f0422`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/39f04228b6270a5d67c31dfa0aa918b6fa5395f1))
* Blupdate testcase and add cli ([`18d5a0c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/18d5a0c231608c80e4db904897c18b9314221fd2))
* **serializer:** Empty line serialize correctly ([`e906287`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e906287f36499accf356aa667f01dc84648194c0))
* Import bonltk only when in use ([`a7e5b48`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a7e5b487d65e2ba12440ecc1c9a28cfc5e650ce4))
* Import bonltk only when in use ([`3ecd475`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/3ecd4751353191f0c37555ac5fbcf8897030039e))
* Return local path to downloaded pecha ([`e91fb4d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e91fb4d5946c497c409dbef1ad26bfa5763097a4))
* Return local path of downloaded pecha ([`fae9e58`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/fae9e58260bfdc73b3d7f37298012283fc26f079))
* **hfml-serializer:** Pagination needs to serialize last ([`468191b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/468191b536403c12c3775231b9fd90c11e5dbeac))
* Small bugs ([`a1b1016`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a1b1016d78caccfc0b86f82e477c8fd8b0954f8a))
* **pagewise:** Pagewise obj created ([`2480e03`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/2480e033c43b5129375cddc56f69025f3a8d70d1))
* **hfm-formatter:** Durchen parser added ([`a4bdd15`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a4bdd15f08f94be407811219e8f8d3e1f4d82eae))
* **serialize-base-module:** Empty line serialize correctly ([`cb4ebca`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/cb4ebca1ad95871c2a441dd034ed68a1cb8775bd))
* **formatter-basemodule:** Pecha without text formatted correctly ([`ff5dee2`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/ff5dee213eb7a29a7a58f5717f5f593bd321b073))
* **hmfl-formatter:** Empty line formatted correctly ([`5fcbe87`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5fcbe87a23260e28e95a1032e8c766d6f1cc790e))
* **epub serialze:** Break after 500 syllables ([`8d93203`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8d9320337029a232328dfcdf21ddb166a3f4f37e))
* **catalog:** Move catalog manager into catalog sub-pkg ([`fb6b084`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/fb6b08442982c0a8aa0e49c862261ffed702d9b4))
* **catalog:** Download corpus cli ([`69b82e6`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/69b82e61b926fa25cc71ecc151caed2c0b4f7eef))
* **catalog-storage:** Get base of all pechas ([`878a31b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/878a31b87c3c4998ec30fce2c1db60443a26c737))
* **github:** Create_file to accept org and token ([`7bf1562`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7bf15622e57af244363e59d5c0f69e01ffb092a1))
* Github helper funcs to work on any org ([`b3aff03`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b3aff036bfbbd8bdcd69e3be1819575e5bfba8f2))
* **formatter:** Missing kwarg metadata ([`051ca1b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/051ca1bdcb795e2422bccf4fecd8355232f68e62))
* **catalog:** Create orphan branch for each layer ([`4ff76f7`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/4ff76f768507ac242ce511e85414b8e0cabcebd2))
* **formatter:** Add source metadata ([`1b2bbe8`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1b2bbe8e7790555e9f73974977a095d37e626390))
* **catalog:** Add hfml item ([`81a982a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/81a982abc59283d8a7e95f999f8fb9ee6f33d53f))
* **serializer:** Disable line-number for epub ([`3ed677e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/3ed677ebb4ef221dbceb1aba4dc5db6a5fce26c6))
* **github-utils:** Create prerelease and return asset download url ([`2b84ee3`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/2b84ee39158e29b10a9a704dc42583966fbaa409))
* **epub-serializer:** Return serialized epub path ([`7d3e8a9`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7d3e8a9700d498cb347dfc52ce1ab0572c74ffeb))
* **test:** Skip the hfml_serializer test for a new release ([`25fba24`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/25fba241d4b1e94b08f2c96b300923dbe8009902))
* **serializer:** Unified opfpath to opf_path ([`9646b34`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/9646b3450c73ab26736f3daf6ebb8ab104b61cdd))
* **hotfix:** Pecha_id as arguments ([`e288b1d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e288b1dc7524da4b1dad383775a791cbad14bd1b))
* Improve log message ([`338e661`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/338e661581d30bb4bf427131cd21a2e70d9ab92d))
* **formatter:** Fix sub topic nested list ([`f22dcd1`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f22dcd1c54e2816e96ee2ba58a5a232c6abc7d10))
* **cli:** Import error ([`218c2bf`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/218c2bf6006ead18305a70b2db88fae4c37d6805))
* **hfml-serializer:** Save hfml text in original filename ([`2969d0a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/2969d0ad63ee0be8a198657da8ff87bd739b5b49))
* **hfml-formatter:** Add vol_id to filename mapping to metadata ([`b67022a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b67022a78c10fdddc8d3043184f4899db0263952))
* **hfml-formatter:** Archaic regex pattern ([`314088d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/314088d08d0507ff9533d173297f483de089d857))
* **formatter:** Create Global2LocalId object for every vol ([`1c1f4cf`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1c1f4cf468199f24693dd84d2dee356fe6898801))
* **serializer:** Add serializer method hfml and typo ([`d80d71f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d80d71f8bfca74c8106c87a42bce6819388b27b7))
* **cli:** Not defined 'result' ([`9ac51cc`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/9ac51ccdceac1ccc598a1ec461c7c7a039d1a621))
* **epub-serializer:** Hfml modify ([`97ddde2`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/97ddde29cf2891b2a9992b43818d98a37e97ea8c))
* **cli:** Add hfml-serializer ([`8260fe9`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8260fe9bd83fac0f2e22be1f77bf26e151ec2281))
* Extract pecha_id from opf_path ([`444de8b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/444de8b3f104dd3f9b2552126995fc5a302db3d3))
* **hfml-formatter:** Change id to id_ in create_opf method ([`a5e2fa7`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a5e2fa730583e509530b467e98559935a73214e4))
* **epub-serializer:** Remove redundant pecha_id in serialize method ([`0a95fd0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0a95fd0e0e971be776b4f768957342a978eec196))
* Add serializer output_path ([`a62d71d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a62d71dfc3893150ae3eb3830837640836f37911))
* Missing openpecha config ([`d3d3d87`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d3d3d87aa8ae39f95d82aa5cf16bd7b1463d245b))
* Missing openpecha config ([`f94839d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f94839d6bf4f3588e79a3604a41f30a696a24898))
* Compatible of hfml formatter and serializer ([#66](https://github.com/OpenPecha-dev/openpecha-toolkit/issues/66)) ([`1ca18ce`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1ca18ce0343cf56a3930a2ac78365d5bb5c7ed0b))
* Change id to id_ ([`62e8cb6`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/62e8cb6efb0a1e76c47f8ea93329389f70536c3f))
* Add output_path optional for format command ([`0c9dfba`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0c9dfba48cd1032824d3c94e9498607f273b4e81))
* Bug in loading and indexing old_layers ([`8418916`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/84189163e752685a67fd7181504ef7c01a06156a))
* Formatting index layer ([`0f6b9c1`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0f6b9c15a5d6947fd157999fddf71811d65bb402))
* Imports and dependencies ([`c90407e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c90407ebe228ef89aea3957718436d4b981efff9))
* Remove openpecha cmd config ([`43f60a1`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/43f60a1890c857db65df86c1baea8c20e82adee2))
* Test data ([`c9dad88`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c9dad88965d07ac4137ae3e8c06236fd12ff8757))
* Add local_id ([`de76e5b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/de76e5b40c38ec60d73298454fdf8f8e810f1917))
* Accessing layer component ([`5cb2f7f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5cb2f7f97124141b62d0d7f02602fa8e834c630a))
* Remove id from annotation ([`4f8611d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/4f8611de919206ee0babd340f4ef624abc8dd3b6))
* Vol_id is optional to get_base_layer ([`ca4a2b7`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/ca4a2b7bdfd9fcfe4205e7cb81d6244e04945cbf))
* Passing text_id from cli ([`4251f9b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/4251f9b7577868f07af5972775c601cc168f9e83))
* Get page number from image file name ([`e2517e3`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e2517e3fed4ac997357d2c4d98643a5879fb87a3))
* Info file + version bump ([`777195b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/777195b23ec9985024f0e5143447cd9da396d82a))
* Image number contains c + version bump ([`8d9f512`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8d9f51270e63f4b47fc3be2d01af85d57a70ee9c))
* Invalid page number ([`8dfdbd1`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8dfdbd1a646881ef5d7d799e1304d7e14ef471ba))
* Page no. with sides (a|b) ([`140bc32`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/140bc3252cc05ea65253bd31ff592a9d2afd4372))
* Page no. contains 'a' ([`2250110`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/225011086aa698b2f7df5af7486171e7cf5ad803))
* Bug in custom last_id ([`24a119d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/24a119d8d3581ce52c5f81b5f6757119c78e4cdf))
* Update last_id after 5 works processed ([`8f6244b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8f6244bab1b676dc2b578cf2dbd675a1ce9c3ae5))
* Ocr-formatter first page index + version bump ([`faa4928`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/faa492865987bd48f3de3095e819bc3e1bf2ac25))
* Ocr-formatter test ([`5413b67`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5413b67fe5969636cc0fc9ebf75cdeced7dc1535))
* Page number ([`6c69f22`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/6c69f221935a113f3b38463265b32ce1f086e8a2))
* Missing new line at end of batch.csv ([`2a48cc1`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/2a48cc1b19c48ba4c509ebc96645b73990d2d9eb))
* Remove error log file at begining for run ([`601d94a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/601d94a889d5c108143036037495515436dc8814))
* Cct return ([`d827a4a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d827a4a2f3a8e1e96f15edb01bbaa62c32b4e718))
* Parent dir doesn't exits ([`bc500b1`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/bc500b1e9126de92ba8245d0b0dd4037c3edf23d))
* Remove file error ([`7d626c4`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7d626c4e270634b43f642dc6667ee89207af48e3))
* Line start with newline ([`850d3da`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/850d3dac098607b26221d89341b8b4bbf96e8611))
* Return correct cct ([`e8cb243`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e8cb24396051720a1d4c26b9129a9558b7a6169d))
* Shifting n_chars bug ([`4e493f5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/4e493f55c148efe01ae66032c06b0ec3e6bfc21a))
* Flags incorrect text id ([`ff4aa63`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/ff4aa63bf422451aac3a863924b29172661964eb))
* Bug in shifted annotations ([`92352f2`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/92352f2b2d6cffcc44631fe9e5fded0f539a091b))

### Documentation
* **core:** How to add base and layer to openpecha ([`15f96f5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/15f96f5aca6e1c4112174ba5da614bca012f717d))
* Add base and layer to pecha ([`18a1571`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/18a1571837ea9c56b0c1620737d78b4294911483))
* Add assert in add annotation in layer ([`5347fb4`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5347fb41ab669c5152e501f180c8a5d078243b81))
* Fix docs src path ([`23a2a49`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/23a2a493148e33b38242fba84ee6249fb56db065))
* Add managing layer docs ([`a8bb38a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a8bb38a50390d43c05169dcb7ab33244f8e940d2))
* **annotations:** Fix correction shema and tutorial path ([`d0cd410`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d0cd410d065d9e1ab2063ed1936566cd8c37fee0))
* **annotations:** Add examples and test ([`d45fd71`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d45fd719dfb68287d3208292f26cfd162b5fd7a5))
* **annotation:** Add json schema build script ([`c2a066d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c2a066dc5bb1a4476cb35bf6645fdda1d39bc328))
* Add citation schema and example ([`abb8ad1`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/abb8ad17fe2e13481bb12a6b64236dce1e17a66a))
* Add index layer example ([`603fb00`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/603fb00d1f0fc02177a086d14f23e1a4b38f6061))
* Add annotations types ([`4489e1e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/4489e1e6aa6b64b8cf466a170a584419bdb4eed3))
* Add annotations page ([`910f8c3`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/910f8c3a32e3c862cbf7fbe316daeca555bb8795))
* Setup mkdocs ([`e5c322e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e5c322e0f41da6f979462224cbf182029a4101f5))
* **alignment-transifex:** Improve documentation ([`353175a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/353175a144e3c12f9924eb51f121b69b145599e8))
* **alignment-transifex:** Add doc_strings ([`6a7fab5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/6a7fab5fd815db4e840b24a9de766cfe7b05d337))

## v0.7.83 (2022-04-01)
### Fix
* **corpus-download:** Skip downloaded pecha" ([`f42e150`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f42e1500e3b714dc702c90d038fe465939552739))

## v0.7.82 (2022-03-31)
### Fix
* **corpus-download:** Use authenticated requests session ([`f0fe570`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f0fe5706591f452559c85a2e3d2f129ef50b278e))
* **corpus:** Get gh token for corpus download ([`94e3188`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/94e3188637c4cf7a53e0945105705463f8e03ceb))

## v0.7.81 (2022-03-30)
### Fix
* **download:** Download suggestion implemented ([`5dffcd6`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5dffcd646421ce04cafc427caf39b3541f7b8ef9))
* **download:** Base text url updated ([`db1d18b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/db1d18bd664fc85ce5aab146de4f696b78dcaf1a))
* **doc:** Documented download function in corpus module ([`f381a3f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f381a3facf70596e82d6319c292dffa1b4a9c8f7))
* **corpus:** Download corpus module compeleted ([`8b9cc73`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8b9cc73849015cfeaaa13336d3b2af881f677d4f))

## v0.7.80 (2022-03-17)
### Fix
* Add missing __init__ ([`3adacbc`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/3adacbce184bff0ed41f3b723ac5737aa328a7e9))

## v0.7.79 (2022-03-17)
### Fix
* **cli:** Transifex imports in cli ([`de530cf`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/de530cf23fc2438223e9fc12e33e9d362fef868b))
* Typos in cli ([`c8b9183`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c8b91838ce678e9cf3e658c8c77ce27d30961cf7))

## v0.7.78 (2022-03-17)
### Fix
* Missing __init__ file ([`b1ddca8`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b1ddca841054de8e226f09331dacaab4aec313fd))

## v0.7.77 (2022-03-17)
### Fix
* OpenPechaFS path ([`b99a041`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b99a04114a91310685759c416447d5723427219c))
* Add cli to count non word and save in meta.yml ([`5ac97c5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5ac97c58ac148e49415436f92ad0387cfb8722ca))
* Twn non_word conter can be added ([`8825625`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8825625c2ad4ef1ff9be25c11aaf72180fa0e152))
* **core-pecha:** Add pecha text quality attr in meta ([`e0a59cf`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e0a59cfb976df3cc33729861f255aa3bad24e4ce))

## v0.7.76 (2022-02-15)
### Fix
* **core-pecha:** Retrive span info ([`0fb51b9`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0fb51b9b59afd35566d32199f8c2f0ee8577673b))
* **core-pecha:** Add update last modified date ([`6285f79`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/6285f7962ed32e7e07c38a4d82881298303d6295))
* **core:** Remove layer_name arg from set_layer ([`e88fe77`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e88fe777ccf6bfa5f2d6267f385376134bd9c3fb))
* **core:** Set base and layer with OpenPecha ([`bb2f6d4`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/bb2f6d469bcf18a6b9c014165c183a0bab0c1006))
* **core:** Layer can add, get and remove annotation from it ([`eed2086`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/eed20864b6f0ff8693d32b4125fa8cbd12cdbae1))

### Documentation
* **core:** How to add base and layer to openpecha ([`15f96f5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/15f96f5aca6e1c4112174ba5da614bca012f717d))
* Add base and layer to pecha ([`18a1571`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/18a1571837ea9c56b0c1620737d78b4294911483))
* Add assert in add annotation in layer ([`5347fb4`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5347fb41ab669c5152e501f180c8a5d078243b81))
* Fix docs src path ([`23a2a49`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/23a2a493148e33b38242fba84ee6249fb56db065))
* Add managing layer docs ([`a8bb38a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a8bb38a50390d43c05169dcb7ab33244f8e940d2))

## v0.7.75 (2021-12-20)
### Fix
* **core:** Add remaining annotaion classes ([`e12b4e0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e12b4e02ab59fb5428cd92541e7e2375c32240fb))
* **core:** Forbid extra parameter in Annotation init ([`1d0ccb0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1d0ccb02922f5bc1f3d2f4736ca63cb9dbfea3b6))
* **core:** Add Citation annotation ([`bd1538d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/bd1538d0dbb7292a538f42152a8d7e09eb90d649))

### Documentation
* **annotations:** Fix correction shema and tutorial path ([`d0cd410`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d0cd410d065d9e1ab2063ed1936566cd8c37fee0))
* **annotations:** Add examples and test ([`d45fd71`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d45fd719dfb68287d3208292f26cfd162b5fd7a5))
* **annotation:** Add json schema build script ([`c2a066d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c2a066dc5bb1a4476cb35bf6645fdda1d39bc328))
* Add citation schema and example ([`abb8ad1`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/abb8ad17fe2e13481bb12a6b64236dce1e17a66a))
* Add index layer example ([`603fb00`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/603fb00d1f0fc02177a086d14f23e1a4b38f6061))
* Add annotations types ([`4489e1e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/4489e1e6aa6b64b8cf466a170a584419bdb4eed3))
* Add annotations page ([`910f8c3`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/910f8c3a32e3c862cbf7fbe316daeca555bb8795))

## v0.7.74 (2021-12-18)
### Fix
* Pydantic version ([`525d980`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/525d980de76622c7e59964ad56742e22593033d4))

## v0.7.73 (2021-12-14)
### Fix
* **storage:** Set remote url ([`23d4570`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/23d4570fd996f61836b8db4e61fb4d6d7599b479))

### Documentation
* Setup mkdocs ([`e5c322e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e5c322e0f41da6f979462224cbf182029a4101f5))

## v0.7.72 (2021-12-06)
### Fix
* **github:** Remove return in update pecha download ([`de1c237`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/de1c237b222029fa271eef98c3a66da14515f8e0))

## v0.7.71 (2021-12-06)
### Fix
* **github:** Setup repo auth when download ([`cf315b4`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/cf315b4f77e2e02b0009a15b20653e4b58ae04a5))

## v0.7.70 (2021-12-06)
### Fix
* **github:** Setup auth for download repo ([`a11c86e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a11c86e9617aeb2a5d71f09e16cbf7dae259df8c))

## v0.7.69 (2021-12-06)
### Fix
* **storages:** Add github repo auth ([`5b8cf8e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5b8cf8e21c5d12ef28d7e23603b4345faebfbafc))

## v0.7.68 (2021-11-26)
### Fix
* **core:** Set default output path to save work ([`9488419`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/9488419a31c4bc046959940f238e87a3e69907c2))

## v0.7.67 (2021-11-26)
### Fix
* **core:** Rset deefault path to save work ([`0b11e67`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0b11e67edd047b3a0c3057d4e8b1af3831e6f03b))

## v0.7.66 (2021-11-26)
### Fix
* **work:** Opwork id can be searched using bdrc instance id ([`a97796d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a97796d550d8b7515cbdb31b8cae614204e0d62f))

## v0.7.65 (2021-11-26)
### Fix
* **work:** Aadd load work from id ([`d75d67b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d75d67b238d00bdde8f3d4f3bb54ad60fdf44e97))

## v0.7.64 (2021-11-25)
### Fix
* **core:** Move work in work sub-pkg ([`691f9ee`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/691f9ee4324dfc91d05fd440a91183ce56ab9e73))
* **core:** Save and load workk from yaml ([`1fba453`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1fba453b9312957cebc33ae896d9dff483d9fc54))
* **core:** Add Work model and test ([`366540d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/366540dab431ac5de303802e617539ff20bf34db))
* **work:** Add work test ([`caf8b52`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/caf8b52bc1b5a46114e9dfbc6f1a410201334f28))

## v0.7.63 (2021-11-25)
### Fix
* **core:** Get id for pecha, work, alignment and collection ([`aa88541`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/aa88541272ab4897f2ff957af1fe1e46c4a4fe55))

## v0.7.62 (2021-11-23)
### Fix
* **github-storage:** Rename publisher to storage and add and remove file ([`557f5d8`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/557f5d80ff2406cfa506d1b5ff5a3e8292888b88))
* **publisher-github:** Remove and get repo ([`550c486`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/550c48643d794eaf5cc076112d28a78bb91a3a25))
* **publishers-github:** Aget dpecha description from about prop ([`93a341a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/93a341a0b11215dae38a1466edf66af0bedf82b3))
* **publishers-github:** Cimake path optional when remove pecha ([`6c004f0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/6c004f069c175b7d40b6b4071b28c1ae4ee55cec))
* **core-publisher:** Add base publisher class ([`7746060`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/774606092305123223b887b4534174b733a8f03a))

## v0.7.61 (2021-10-29)
### Fix
* **hfml:** Page annotation updated ([`a7eec5e`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a7eec5e12ddce18d0ed1dbb732a42cf48f94dd09))

## v0.7.60 (2021-10-29)
### Fix
* **test:** Test data included separately ([`e951fca`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e951fca4e36d7ef17d2dd62e0103375ee77d1879))

## v0.7.59 (2021-10-28)
### Fix
* **alignment-transifex:** Set transifex project repo url ([`26bae15`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/26bae15fe01466aae0498231242b2628f3a9e0d1))
* **alignment-tmx:** Add relation to alignment.yml's segmentsource ([`1a00972`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1a00972e0b171774c09700c39522dacf819308ea))
* **alignment-tmx:** Add relation to alignment.yml's segmentsource ([`db65e41`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/db65e41cd2edf4d00de320b2eefb58374eec32db))
* **alignment-tmx:** Add relation to alignment.yml's segmentsource ([`b96adc3`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b96adc3923ba700ffd132c6cb66da9a2bf6ceb51))
* **po:** Po view look up done on relation ([`1d81623`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1d816239cc95dfe65a4833d2dad36f7fbcf08724))
* **alignment:** Add import alignment cli ([`dc8aff0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/dc8aff09f5e0533cd4ba4e9b35eca0584c458a23))
* **alignment:** Return alignment repo path ([`7d0bf1c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7d0bf1cce3ad813a5c6734dc8366033f9730b8da))
* **alignment:** Default branch is master ([`413acbe`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/413acbe47b1f28696044bb5d04a1ccd371721e6c))
* **alignment:** Return project id and alignment title ([`c54b82d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c54b82d805d67b6368f18cd9e6d43fa2a01df405))
* **alignment:** Base in exporter ([`4ce9e99`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/4ce9e99d2520d6af66a1a457d7f3185d8b0a89ce))
* **alignment:** Load metadata ([`876b817`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/876b817c952d5061f6b30839a7b111640fb170c7))
* **alignment-tmx:** Add tmx parsers and po parsers ([`e462628`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e4626286024eff5220803b5cd4a854147b2015cb))
* **alignment-tmx:** Add tmx parsers and po parsers ([`cb7703c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/cb7703c56539b7074a02a85b9f934ef1cdce0272))
* **test:** Po test data separated ([`3a92be9`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/3a92be9bc03127e07e0e7a56bf1e7b893b6c509c))
* **test:** Po test data separated ([`461e0f1`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/461e0f10aa07ba3d81939e7c515816a6b18dbfcc))
* **po:** Language added while po export ([`8fcb59c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8fcb59cfd08f45b560bce6faac204c918003987c))
* **alignment-tmx:** Add create alignment from tmx ([`049d970`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/049d9708484de52ccf0548d7f560258d337a05ef))
* **po:** Po exporter updated ([`e25d1db`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e25d1dbd347ca315b4e1373d07f4b5c986f9e53e))
* **alignment-tmx:** Add create alignment from tmx ([`ed3588c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/ed3588cf536a4c320aaacf9512f2652560a108a1))
* **alignment-tmx:** Add create alignment from tmx ([`8c2c592`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8c2c592fd28d78377fd2876fa1a078e2b7f608ff))
* **alignment:** Get po view added ([`b832737`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b8327379e876dd94bb0a4c5df7aed026c16c3552))
* **po:** Keyerro bug fixed and functions documented ([`d7ead02`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d7ead026f0f8a4c87b11347a5493481d079fc290))
* **test:** Test code updated ([`dbbae52`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/dbbae523a692e541f39d7ab9105457ab982d4a61))
* **alignment-transifex:** Add traget language to the project ([`8a89e01`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8a89e017b7058862039382cc9ddd04184681b151))
* **po:** Po view populated to po branch ([`226d36b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/226d36b91c4179286f898dc0d6a2fa8844b1e37c))
* **bitext:** Bitext exporter implemented ([`538c3e7`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/538c3e7a8ce38ad8d60d80940225d1286f359a6e))
* **alignment-transifex:** Add TM to transifex project ([`7d861f0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7d861f0d27407f9bb10ad04512c0c3837f915e2f))
* **po:** Po exporter implemented ([`26bd01d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/26bd01d34ca6770b96919ca35d3e19cf5863177e))

### Documentation
* **alignment-transifex:** Improve documentation ([`353175a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/353175a144e3c12f9924eb51f121b69b145599e8))
* **alignment-transifex:** Add doc_strings ([`6a7fab5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/6a7fab5fd815db4e840b24a9de766cfe7b05d337))

## v0.7.58 (2021-10-20)
### Fix
* **blupdate:**  typos in update span ([`8d089f5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8d089f51f58d2a0a59afa252df36fedc6a9361be))

## v0.7.57 (2021-09-15)
### Fix
* **test-formatter:** Pedurma testcase updated according to changes made in formatter ([`8de3f01`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8de3f01fcb9f5f0e7f9a236186336624f019ff31))
* **pedurma:** Formatter and serializer test case updated ([`d965422`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d96542236a1b8db7ce04d3e8ead55608073aa8b9))
* **pedurma-formatter:** Pagination annotation changed to hfml format ([`bb80bbd`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/bb80bbd276cc1d0cf72a167c85bffab62838cefb))
* **pedurma-serializer:** Doc string added ([`b9613ae`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b9613aee8dc51a25a91b18bb6a4461e8267492c8))
* **test:** Merge conflict resolved ([`9bb1a6c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/9bb1a6cf97cb350fd9711ea989ffd900a9552af1))
* **test:** Test case added for pedurma formatter and serializer ([`64d2b98`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/64d2b988b95ba1107c9ea3c3a5c83814a05abf20))
* **pedumra:** Formatter for preview text and serializer of diplomatic text completed ([`d7ee2f5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d7ee2f5f34c0967080365a7e2316329ab69b835b))
* **pedurma-formatter:** Integration completed ([`5691391`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5691391c86c1d38fd5dc95a4a4936a9fa6b23185))
* **pedurmaFormatter:** Pedurma note formatter and serializer added ([`c39863b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c39863bf0bb6efd16dc140d9622c0a1ad93897ef))

## v0.7.56 (2021-09-15)
### Fix
* **hfml:** Self.dump replace to dump_yaml from utils ([`b96eb87`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b96eb87a158074ab245e7569fcdceae9575f4291))

## v0.7.55 (2021-09-15)
### Fix
* **google-ocr:** Flag added if meta required or not ([`1a80bc2`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/1a80bc29343a44df9c46b541a4b4351797b49c9e))
* **google-ocr:** Post processing for page is done to google ocred pages ([`62db212`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/62db212b002b41acdf1f4fde134e7a2abc4373c3))

## v0.7.54 (2021-09-06)
### Fix
* **save_page:** Starting of text in same vol updated properly ([`eb273e0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/eb273e0d4db114ee778882ecb7a0cfbbb917dde5))

## v0.7.53 (2021-08-31)
### Fix
* **proofreading:** Span of sub text is update bug fixed ([`434638d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/434638db2d9f28408cb68bdac4b751a9b03525d0))
* **proofreading:** Subtext start update bug fixed ([`0fbeb4d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0fbeb4d668d222f049a31b768200d48b34d3f594))

## v0.7.52 (2021-08-27)
### Fix
* **docx-serializer:** Font family included in styles ([`f794ca5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f794ca5ad23483ae92ca0ce15fb2ead1ba990be8))

## v0.7.51 (2021-08-27)
### Fix
* **editor-serializer:** Multiple tsawa and citation type supported ([`d65835d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d65835dfdcb20d8bdd8a50f2dbe7ea448ac1076c))

## v0.7.50 (2021-08-27)
### Fix
* **serialisers:** Unify aserialize api ([`3faa1b5`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/3faa1b51eb3aad2475ec846d4457551590364fbc))

## v0.7.49 (2021-08-26)
### Fix
* **epub:** Enum used to avoid hardcoded condition checking ([`306a9c0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/306a9c0dbe7e42787fe3481ec3af7f88a9d2714e))
* **editor-formatter:** Ann type supports ([`b8a5f5a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b8a5f5ab330ed5918f98008933b9147e797c3d3a))
* **docx-serializer:** Docx serializer formatted as class ([`024f19a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/024f19aa890d26f34cbeb8da3c4fa7503f901dfa))
* **test:** Pecha asset added ([`f97fa31`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f97fa3140e3c1d35fcbddd528c951fa8c7e0246a))
* **test:** Chapter and booknumber added ([`8d3a56c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/8d3a56c3039bfcfb1c025d4cf1a9ea9575f9a32a))
* **testcase:** New test case added ([`fff431f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/fff431f09dbfc09d2d08fe4ce410d8b824ebfffb))
* **epub-serializer:** Multiple type of citation and tsawa annotation supported ([`c35d7cf`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c35d7cf2f5302d75e43a306e9ff3121a01008c55))
* **testcase:** Test case imporved ([`97d3b4b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/97d3b4bba62167afa87f3aa5b7d2520acbfc933d))

## v0.7.48 (2021-08-24)
### Fix
* **epub-test:** Test case updated according to new book title tag ([`d2c0d7f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d2c0d7fdbc017d031a4166673cb61034b44e0ee1))
* **docx:** Test added to docx serializer ([`97c1c87`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/97c1c8780f9f74655ab987030561141718d03fe5))
* **docx:** Docx serializer added ([`c26b0cd`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/c26b0cd9766245c45757d696e8ec96ef75706c74))

## v0.7.47 (2021-08-17)
### Fix
* **hfml-serializer:** Subtext serializer bug fix ([`01d31c2`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/01d31c2d7fd7952e80bde77d27c35c67c0fa309a))

## v0.7.46 (2021-08-13)
### Fix
* **proofreading:** Branch bug fixed ([`5702684`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/5702684a0ffa35d7210c64db3105833769d711f2))

## v0.7.45 (2021-08-13)
### Fix
* **cli:** Also check for remote branch ([`224e170`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/224e170d087debb377645b8be04bd343ef97d652))
* **cli:** Pass repo in branch evaluate ([`f3feebd`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/f3feebd6691b1c1df9eb3fe29dc3ffc25f57bf05))

## v0.7.44 (2021-08-13)
### Fix
* **proofreading:** Branch option and sub text update included ([`af04c6f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/af04c6f29a0cff16353118a62a25b065af94a446))

## v0.7.43 (2021-08-12)
### Fix
* **download-pecha:** Set fallback branch ([`0286d53`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0286d53a803a2afa45b44907a7da0b6c235a6351))

## v0.7.42 (2021-08-12)
### Fix
* **proofreading:** Vol info return list of volume details ([`b8164a6`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b8164a669c24ce014f51d6ae7feb00d5cc47c8b9))

## v0.7.41 (2021-08-12)
### Fix
* **proofreading:** Method to assist proof reading editor added ([`d874f91`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d874f9170e59252607194812d27cfea072d63971))

## v0.7.40 (2021-06-22)
### Fix
* Pagination layer name typo ([`29b6ede`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/29b6edee2b7ddcf06a1fb996175a41ad004e672b))

## v0.7.39 (2021-06-02)
### Fix
* **utils:** Yaml loader and dumper is changed to Csafeloader and Csafedumper ([`da8ff8b`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/da8ff8b386055357be71db25a7d7f422b554dbdd))

## v0.7.38 (2021-05-28)
### Fix
* Raise exception for pecha doesn't exist ([`69aa954`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/69aa954f3970b1e2cfd8e740e24d308ec86c9154))

## v0.7.37 (2021-05-25)
### Fix
* **core-pecha:** Reset layers by reading components ([`031b8bb`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/031b8bb037c4fceb65b4010a212ed0c220ad303c))

## v0.7.36 (2021-05-21)
### Fix
* **core.pecha:** Add rest layers ([`7d25a4a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/7d25a4a36f47c98a2520d1b9c71bddf7a1cbc12a))

## v0.7.35 (2021-05-20)
### Fix
* **test:** Test for serializers are separated ([`0ed687a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/0ed687a0d8295de89144c68b173460370bdbbc69))
* **editor:** Chapter serialize correctly in editor ([`cd2572a`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/cd2572ab7f73e61ddabb00d70f32f6d5d6c8c170))
* **epub-serializer:** Alt option added for img tag of credit page ([`540c6fa`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/540c6faf86745ae0e1f369126a74b616feff815c))
* **epub-serializer:** Verse type annotation style changed ([`788ecab`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/788ecab70cd108fc65dc64da8fd9774e24568f6f))

## v0.7.34 (2021-05-13)
### Fix
* **serialize:** Text span bug fix ([`29ae052`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/29ae052deb27b14d707f266367ad9b5b3b4434e5))
* **hfml-formatter:** Topic end span for last page changed ([`a1d36de`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/a1d36de32e8c426ef78421379e5825c82f0f18db))
* **text-formatter:** Text-formatter added ([`b78698f`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b78698fa71487bc44f01c8468010717626a140b0))

## v0.7.33 (2021-05-06)
### Fix
* **serializer:** Line annotation removed ([`e3af107`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e3af107c777b8967260a14723a37cf4ee36dfafa))

## v0.7.32 (2021-05-05)
### Fix
* **epub-serialise:** Skip embedding ibook specification if epub doesnt exist ([`07b4acc`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/07b4acc747556fb39b7eb37cc6a05c817cf048e3))
* **epub-serializer:** Renaming approch changed ([`ec620f4`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/ec620f4e53f48a22a2dc749ace4396c39becaf44))
* **test-serialize:** Epub serializer updated ([`d117d86`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d117d867d87dc3771412d442a6463370ba7380c2))
* **epub-serializer:** Ibook specification for proper font embedding included ([`107cb69`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/107cb691e03ef9a93c08e4ed5c13dc2279cb24ac))

## v0.7.31 (2021-04-30)
### Fix
* **hfml-serializer:** Page index changed to imgnum ([`d83a86d`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d83a86de12a0bdb6325a9a6ae4ce5ba9531c0706))

## v0.7.30 (2021-04-27)
### Fix
* New release ([`e16260c`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/e16260c6f9c024ab78661c3810581e33a1297254))
* **serializer:** Index layer passed as parameter in order to avoid multiple loading of it ([`61a53ae`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/61a53aed4721e03421dd26eb46c2d06898843b9a))
* **hfml-serializer:** Extra line at the end of pages bug resolved ([`395ec95`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/395ec95ab0f29be7b665654ffc2187c873e2bf89))

## v0.7.29 (2021-04-20)
### Fix
* Ann start ([`aa0cc38`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/aa0cc389507037590e654e99bf31240109bbfba0))

## v0.7.28 (2021-04-20)
### Fix
* Ncreate  single ann as a group ([`b78bcf0`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/b78bcf0c53b9e5b2c34d436688f0d950c616c7d2))

## v0.7.27 (2021-04-10)
### Fix
* Specify upper and lower bound for deps ([`cb2a629`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/cb2a629c86b954d990b1a063b4c4d86d1ec7fa08))

## v0.7.26 (2021-04-09)
### Fix
* **epub-serialize:** Added front page generator using meta data ([`6f48523`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/6f48523feb34686229f2ebbff2f58e21126fc2e0))
* **epub:** Set default toc level if exist in serialized html ([`d475e15`](https://github.com/OpenPecha-dev/openpecha-toolkit/commit/d475e15f4cd0daa0ead7e3ff049f2ea92c2d6c03))

## v0.7.25 (2021-04-08)
### Fix
* **editor-formatter:** Skip grouping if layer is empty ([`bd651cd`](https://github.com/OpenPecha/openpecha-toolkit/commit/bd651cd04cd51540a81f484db2663d6a36606cc9))

## v0.7.24 (2021-04-08)
### Fix
* Exlude alll ann attrs with value none ([`c2408e4`](https://github.com/OpenPecha/openpecha-toolkit/commit/c2408e4e6f9ff7b1bb15dfa448006fe4773d97ea))

## v0.7.23 (2021-04-07)
### Fix
* **google-ocr:** Add imgnum to page ann ([`76ccc8d`](https://github.com/OpenPecha/openpecha-toolkit/commit/76ccc8dbb7f08fd67bea1c6ad16459d96e64bd50))

## v0.7.22 (2021-03-29)
### Fix
* Create layer if doesn't exist ([`af3ab83`](https://github.com/OpenPecha/openpecha-toolkit/commit/af3ab83833f36198308389184ac368d84b9fcffc))

## v0.7.21 (2021-03-26)
### Fix
* **verse-annotation:** Isverse attribute of verse type annotation changed to is_verse ([`4173c1a`](https://github.com/OpenPecha/openpecha-toolkit/commit/4173c1a66d9c3f68dbc7a38fdb6e1c3b56d99d69))

## v0.7.20 (2021-03-26)
### Fix
* **test_serializer:** Testcase added for editor serializer ([`2c4d653`](https://github.com/OpenPecha/openpecha-toolkit/commit/2c4d653c0e61e4830d997de449cc7742092badbc))
* **editor-serializer:** P tag introduced to verse components ([`7d4800f`](https://github.com/OpenPecha/openpecha-toolkit/commit/7d4800f9674cd7d18bbae089085f783248e63253))
* **editor-serializer:** Footnote serialization enabled ([`53149e3`](https://github.com/OpenPecha/openpecha-toolkit/commit/53149e37c2fbc76c00f7baad787e7afd6abdee53))

## v0.7.19 (2021-03-26)
### Fix
* Grouping root-text and find verse ([`a1a2484`](https://github.com/OpenPecha/openpecha-toolkit/commit/a1a248452f29b5dc38fbfb6614bc7149e0c859d2))

## v0.7.18 (2021-03-25)
### Fix
* Editor parser span ([`9242571`](https://github.com/OpenPecha/openpecha-toolkit/commit/9242571a9f86f1f8860ac3e3367cf052be1a298f))

## v0.7.17 (2021-03-25)
### Fix
* Radd missing layers and improve test ([`f336aef`](https://github.com/OpenPecha/openpecha-toolkit/commit/f336aef99808242a1a69bd9c61abb6940c2b4bb1))

## v0.7.16 (2021-03-24)
### Fix
* Return output from editor serializer instead of saving ([`c6297c0`](https://github.com/OpenPecha/openpecha-toolkit/commit/c6297c056203e932af31edf915ef33a0f1357321))
* Author css class ([`583d688`](https://github.com/OpenPecha/openpecha-toolkit/commit/583d6885a1714fdc9c3fa2c71978149b4070f9ee))
* **editor-serializer:** Added special serializer for editor ([`0de0dbf`](https://github.com/OpenPecha/openpecha-toolkit/commit/0de0dbf4667e78e3e3d39f70cbcf51f21d51c00a))

## v0.7.15 (2021-03-23)
### Fix
* Aupdate base and layers ([`96c95b8`](https://github.com/OpenPecha/openpecha-toolkit/commit/96c95b8c3db9d002121806b957a20380b8bba155))
* Add editor outpur parser ([`ef85a5f`](https://github.com/OpenPecha/openpecha-toolkit/commit/ef85a5f1e8bebe19ec0cf6eb05ef394f2f783dd2))

## v0.7.14 (2021-03-23)
### Fix
* **epub-serializer:** Removed credit page layer n added credit page img tag after first author ([`0342a17`](https://github.com/OpenPecha/openpecha-toolkit/commit/0342a179862aa663fe38059290bf67332bb3f1e8))
* **epub-serializer:** Removed credit page layer n added credit page img tag after first author ([`044e119`](https://github.com/OpenPecha/openpecha-toolkit/commit/044e119ecdc8638b243128e15788d51307636f19))
* Toc level variable changed ([`c5c07af`](https://github.com/OpenPecha/openpecha-toolkit/commit/c5c07af6d5425c7c2640a2102874c22ad4b1a1e5))
* Toc level variable changed ([`3734339`](https://github.com/OpenPecha/openpecha-toolkit/commit/3734339fee49d463211f0ca67dfb316d3f30181d))

## v0.7.13 (2021-03-17)
### Fix
* Cbranch checkout in pecha download ([`d89c607`](https://github.com/OpenPecha/openpecha-toolkit/commit/d89c607f5d78d92975833b1ec9bb92cefe99da7b))

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
