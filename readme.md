# UndertaleKrStringMod
## English
이 부분은 영어 버전 Readme입니다. 한국어 버전은 아래에 작성되어 있습니다.

A tool to modify strings of [Altar.NET](https://gitlab.com/PoroCYon/Altar.NET) projects, along with additional tool(s) to ease the manipulation of Korean translation mod by [Team Waldo](https://blog.naver.com/PostList.nhn?blogId=teamwaldo).

Currently just a viewer to show `strings.json`, but that will (hopefully) change soon.

#### Why not use UndertaleModTool or other tools easier to use?

[UndertaleModTool](https://github.com/krzys-h/UndertaleModTool) is a great tool, but it failed to run on existing Korean mod when I tried. When I first had my DETERMINATION to start the project, I was thinking this job was going to be easy once I find the right tool. When UTMT failed on me, I still had no idea whatsoever how this journey would go. I didn't know how popular the project was. I didn't even know whether the project was still active or not. I did not care to file a issue report because this was going to be an easy job. Running Altar.NET was honestly quite a challenge to me, too. The route I took was possibly not the best one, but after a week or so of poking around, here I am, ready to release my first github repository that is of any use.

#### I can't read Korean, but it sounds interesting. Can you tell me what it does?

Currently all it does is viewing and searching `strings.json`, but soon - that is, assuming I did not slack off on updating this readme - to be implemented is simple caching/indexing the strings in `code/` with `grep`, select a file to modify, and then modify the lines in the file.

"Additional tool" currently implemented is deleting/inserting "padding spaces". In Team Waldo's translation mod, hangul transcripts take two horizontal space, probably due to square nature of hangul transcript. It's cumbersome to take care of it every time you edit or search, so I automated the process.

#### Any additional job planned?

Once I get this tool working reasonably well, I will create a modified version of the translation mod. I don't think I can re-translate the whole game. I will probably work for a few scenes and post a video of it.

Currently, I have gone as far as figuring out how the hangul output on the translation mod works. I will try to adopt it to a recent, relatively short mod, as a showcase. I can't say for sure if it's actually possible. The existing TW's translation mod was made for Undertale 1.00-1.01. IIRC, that was GameMaker 8, and for later version, the official Undertale has moved on to GameMaker:Studio, which was, AFAIK, also partly why TW did not continue the job.

### Thanks to

Without any of the works of these people, I wouldn't have even imagined to have the DETERMINATION to tackle on a project like this.

- Toby Fox, of course, for creating this wonderful game.
- Team Waldo, for doing all the hard work of patches and translation from the first place.
- PoroCYon, for creating Altar.NET which thankfully worked with the existing mod.

## 한국어
This is the Korean version of the Readme. English version is written above.

[Altar.NET](https://gitlab.com/PoroCYon/Altar.NET) 프로젝트 파일의 문자열을 수정하기 위한 툴입니다. [팀 왈도](https://blog.naver.com/PostList.nhn?blogId=teamwaldo)에서 제작한 한글화 모드를 다루기 편하도록 하는 추가적인 기능 또한 포함되어 있습니다.

현재로써는 `strings.json`을 읽어내기 위한 뷰어일 뿐이지만, 실제 수정이 가능하도록 아마도 곧 업데이트 될 예정입니다.

Altar.NET 프로젝트 폴더 내에서 실행하면 파일을 불러와서 실행하게 됩니다. **Altar.NET 실행과 관련된 질문은 받지 않습니다.**

#### UndertaleModTool같은 더 쉬운 툴을 사용하지 않는 이유는 무엇인가요?

[UndertaleModTool](https://github.com/krzys-h/UndertaleModTool)도 좋은 툴이지만, 한글화 모드를 불러오려고 하면 프로그램이 뻗어버렸습니다. 처음 이 프로젝트를 시작할 **의지**를 다졌을 때에는 제대로 된 툴만 찾아낸다면 작업 자체는 쉬울 거라고 생각했거든요. 그 때는 그 툴이 얼마나 유명한지, 관리는 되고 있는지도 알 수 없었고, 그리 큰 작업이 아닐거라 생각했기 때문에 이슈 리포트를 작성할 필요도 없다고 생각했고요. 솔직히 Altar.NET을 처음 실행하는 것도 나름 고생했지요. 사실 이 방법이 제일 쉬운 방법인지는 아직도 잘 모르겠지만, 대략 일주일 정도 이것저것 건드리다 보니 여기까지 오게 됐고, 또 개인적으로는 처음으로 대충이나마 쓸만한 프로젝트가 되었기에 깃허브에 공개하게 되었습니다.

#### 어떤 방식으로 동작하나요?

현재로써는 `strings.json`를 보고 검색하는 정도의 기능만 존재합니다. 조만간 `code/` 내의 소스 코드를 `grep`을 이용하여 간단히 인덱싱 및 캐싱하고, 수정할 파일을 선택한 다음, 파일 내의 내용을 수정하도록 구현할 예정(readme 최신화를 미뤄놓지 않았다면)입니다.

현재 '한글화 모드를 다루기 편하도록 하는 추가적인 기능'으로는 팀 왈도 한글화판에 존재하는 한글 문자 다음의 공백을 일괄적으로 추가하거나 제거하는 기능이 구현되어 있습니다.

#### 차후 계획이 있나요?

이 툴이 어느정도 완성되면, 팀 왈도의 번역물을 수정한 모드를 만들어 볼 계획입니다. 게임 전체를 새로 수정하는 건 무리일 것 같고, 일부만 수정해서 영상을 업로드할 것 같습니다.

현재, 팀 왈도에서 한글 출력이 구현된 방식을 어느정도 파악해 두었습니다. 비교적 최근의 짤막한 모드를 한글화 해서 이 툴을 실증해 볼 계획입니다. 게임메이커 8이 아닌 게임메이커 스튜디오 버전의 모드에 적용하는 거라서 장담할 수는 없습니다.

### 감사의 말

이 분들의 작업이 없었다면, 이 프로젝트를 시작할 **의지**를 갖는 건 상상도 못했을 것 같습니다.

- Toby Fox, 무엇보다도 이 게임을 처음부터 만들어 주신 것에 대해서.
- 팀 왈도, 한글 출력 패치를 바닥부터 만들고, 번역을 진행해서 한글 모드를 제작해 주신 것에 대해서.
- PoroCYon, 다행히도 한글 모드 상에서 동작해 준 Altar.NET을 제작해 주신 것에 대해서.
