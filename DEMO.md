# DEMO.md — Jak tuto aplikaci prezentovat

> Scénář prezentace pro publikum, které **nezná umělou inteligenci, Claude, RAG ani Python**.
> Cíl: aby divák za 10 minut pochopil, *co to dělá*, *proč je to užitečné* a *v čem je to chytré* — bez jediného technického pojmu, který by mu nic neřekl.

Aplikace: **t418-py-rag-search-postgresql** — „chytré vyhledávání ve vlastních dokumentech s AI odpovědí".

---

## 1. Jedna věta na úvod (výtah, „elevator pitch")

> „Je to **chytré vyhledávání ve vlastních dokumentech**. Nehledá podle přesných slov jako Ctrl+F, ale **podle významu** — a když chcete, umělá inteligence vám z nalezených dokumentů rovnou napíše **odpověď vlastními slovy**."

Když má divák pochopit jen jednu věc, je to tahle. Zbytek prezentace ji jen rozvádí.

---

## 2. Problém, který to řeší (začněte lidsky, ne technikou)

Nejdřív ukažte bolest, kterou každý zná:

- **Klasické hledání (Ctrl+F, vyhledávání na webu firmy) hledá slova, ne význam.**
  Když do dokumentu napíšete „auto" a budete hledat „vozidlo", nenajdete nic — přestože je to totéž.
- Když máte **stovky dokumentů**, nechcete je číst všechny. Chcete se **zeptat** a dostat odpověď.

> Přirovnání, které funguje na každého:
> „Představte si nového kolegu, který **přečetl všechny naše dokumenty** a pamatuje si je. Nezeptáte se ho na přesné slovo — zeptáte se ho normálně, lidsky, a on vám řekne, kde to je, a rovnou to shrne. Přesně tohle ta aplikace dělá."

---

## 3. Tři pojmy vysvětlené bez žargonu

Během prezentace se objeví tři slova. Vysvětlete je **přirovnáním**, ne definicí.

### a) „Vyhledávání podle významu" (odborně: sémantické vyhledávání / embeddingy)

> Počítač si každý text převede na něco jako **souřadnice na mapě významů**.
> Věty, které znamenají něco podobného, leží na téhle mapě **blízko sebe** — i když používají úplně jiná slova.
> „Pes" a „štěně" jsou blízko. „Pes" a „faktura" jsou daleko.
> Když se na něco zeptáte, aplikace najde na mapě **nejbližší dokumenty**.

To je celé kouzlo. Nemusí padnout slovo „embedding" ani „vektor" — stačí **mapa významů a vzdálenost**.

### b) „Databáze, která umí měřit vzdálenost" (odborně: PostgreSQL + pgvector)

> Dokumenty se ukládají do databáze — jako když si firma vede evidenci.
> Tahle databáze umí navíc jednu věc: **spočítat, jak blízko k sobě dva významy jsou**.
> Díky tomu dokáže i mezi tisíci dokumenty okamžitě najít ty nejrelevantnější.

### c) „AI, která odpoví jen z toho, co našla" (odborně: RAG + Claude)

> Claude je **umělá inteligence, která umí psát text** (příbuzný toho, co lidé znají jako ChatGPT).
> Sama o sobě má ale nešvar: když něco neví, občas si to **vymyslí**.
> Proto to uděláme chytře ve **dvou krocích**:
> 1. Nejdřív **najdeme** ve vašich dokumentech, co se dotazu týká.
> 2. Pak AI řekneme: *„Odpověz POUZE z těchhle nalezených dokumentů a uveď, ze kterého čerpáš."*
>
> Tím ji **uzemníme na fakta** — odpovídá z vašich dat, ne z toho, co si domyslí.
> Tomuhle postupu se odborně říká **RAG** (find first, then answer). Zkratku nemusíte ani vyslovit.

> Silná pointa do prezentace: „Rozdíl je jako mezi studentem, který u zkoušky **blafuje**, a studentem, který si **nejdřív najde v učebnici** a pak odpoví s odkazem na stránku."

---

## 4. Živé demo — přesný scénář u obrazovky

Předpoklad: aplikace běží, otevřete v prohlížeči **http://localhost:8000**.
(Jak ji spustit → viz sekce 7.)

Na stránce jsou tři části: **Dotaz + Výsledky** vlevo, **Přidat dokument + Knihovna** vpravo. V knihovně je připraveno 5 ukázkových dokumentů (Docker, vektorové databáze, RAG, FastAPI, PostgreSQL).

### Krok 1 — Ukažte, co je uvnitř (5 s)
Ukažte vpravo **Knihovnu dokumentů**: „Tohle jsou naše dokumenty. Aplikace je zná."

### Krok 2 — Vyhledávání podle významu (hlavní aha moment)
Vlevo do pole **Dotaz** napište něco, co **není doslova v textech**, ale významově sedí. Např.:

> **„jak zabalit aplikaci aby fungovala všude stejně"**

Klikněte na **Hledat**.

- Nahoře vyskočí dokument **„Docker basics"** s vysokým procentem shody.
- **Zdůrazněte:** „Všimněte si — nikde jsem nenapsal slovo *Docker*. Napsal jsem to lidsky a on přesto našel správný dokument. To je to hledání podle **významu**, ne podle slov."

Procenta u výsledků = **jak blízko na mapě významů** dokument leží k dotazu.

### Krok 3 — Kontrast s hloupým hledáním (nepovinné, ale silné)
Řekněte: „Kdybych tohle napsal do klasického vyhledávání přes slova, nenašlo by to **nic** — slovo *Docker* tam nepadlo."

### Krok 4 — Nechte AI odpovědět (RAG)
Do stejného pole napište přirozenou otázku, např.:

> **„Proč AI někdy odpovídá nepravdivě a jak tomu tady bráníme?"**

Klikněte na **✦ Zeptat se AI**.

- Objeví se **odpověď vlastními slovy** + řádek **Zdroje** s dokumenty, ze kterých AI čerpala.
- **Zdůrazněte dvě věci:**
  1. „Neodpovídá z internetu ani z hlavy — odpovídá **z našich dokumentů**."
  2. „A **říká, odkud to má** (Zdroje). To je ta kontrola proti vymýšlení."

### Krok 5 — Přidejte vlastní dokument naživo (efektní finále)
Vpravo v **Přidat dokument** vyplňte cokoli z oboru publika. Např.:

- **Název:** `Dovolená ve firmě`
- **Obsah:** `Zaměstnanci mají 25 dní dovolené ročně, žádost se podává vedoucímu alespoň týden předem.`

Klikněte **Uložit a zaembeddovat**. Dokument se objeví v knihovně.

Pak se vlevo zeptejte:

> **„Kolik dní volna dostanu a jak o něj požádat?"** → **✦ Zeptat se AI**

AI odpoví z **právě přidaného** dokumentu.

> Tohle je **nejsilnější moment celé prezentace**: „Právě jsem přidal nový dokument a aplikace ho okamžitě umí použít k odpovědi. Takhle si sem firma nasype svoje směrnice, smlouvy, manuály — a hned se jich může ptát."

---

## 5. Proč je to zajímavé (řekněte lidskou řečí)

- **Ptáte se normálně, lidsky** — žádná klíčová slova, žádné filtry.
- **Odpovědi jsou podložené** vašimi dokumenty a mají uvedený zdroj → důvěra.
- **Data zůstávají u vás.** Samotné vyhledávání běží **lokálně na počítači**, bez posílání textů někam ven. (AI odpověď je volitelná — viz sekce 6.)
- **Roste to s vámi:** přidáte dokument → hned je součástí vyhledávání i odpovědí.
- Použití v praxi: firemní znalostní báze, helpdesk, hledání ve smlouvách/směrnicích, onboarding nováčků.

---

## 6. Dvě „úrovně" aplikace (důležité pro upřímnost prezentace)

Aplikace funguje ve dvou režimech a je fér to zmínit:

1. **Vyhledávání podle významu** — funguje **vždy a samo**, kompletně na tomto počítači, zdarma, bez internetu a bez jakéhokoli účtu.
2. **AI odpověď vlastními slovy** — vyžaduje připojení ke Claude (přístupový klíč).
   - **Když klíč je** → dostanete plnou odpověď textem.
   - **Když klíč není** → aplikace nespadne; poctivě napíše „AI je vypnutá" a i tak ukáže nalezené dokumenty a zdroje.

> Stav vidíte vpravo nahoře v hlavičce: zelený štítek **AI: zapnuto / vypnuto**.
> Když prezentujete bez klíče, není to chyba — jen upozorněte: „Teď běží jen ta chytrá vyhledávací část; s klíčem by tady byla i souvislá odpověď."

---

## 7. Jak to spustit (kdyby se ptali nebo pro vás před prezentací)

Vše běží v **Dockeru** (nástroj, který aplikaci „zabalí" tak, aby se rozjela na jakémkoli počítači stejně — mimochodem přesně to, co jsme hledali v demu v kroku 2).

```bash
# spuštění celé aplikace (databáze + aplikace); poprvé si stáhne, co potřebuje
docker compose up --build

# potom otevřít v prohlížeči:
#   http://localhost:8000
```

- Chcete i AI odpovědi? Před spuštěním zkopírujte `.env.example` na `.env` a vyplňte přístupový klíč ke Claude (`ANTHROPIC_API_KEY`). Bez něj funguje vyhledávání, jen bez souvislé odpovědi.
- Zastavení: `docker compose down`.

**Tip na prezentaci:** spusťte aplikaci **před** publikem už předem (první start stahuje data a chvíli trvá). Ať u diváků naskočí okno okamžitě.

---

## 8. Časté otázky a jak na ně odpovědět jednoduše

**„Je to jako ChatGPT?"**
> Příbuzné, ale s klíčovým rozdílem: ChatGPT odpovídá z toho, co se naučil z internetu. Tohle odpovídá **z vašich vlastních dokumentů** a **říká, odkud to má**.

**„Jak to ví, co myslím, když nepoužiju přesná slova?"**
> Každý text si převede na polohu na „mapě významů". Podobné významy leží blízko sebe, takže najde správný dokument, i když použijete jiná slova.

**„Může si to vymyslet?"**
> Právě proti tomu je to postavené. AI dostane pokyn odpovídat **jen z nalezených dokumentů** a **uvést zdroj**. Když odpověď v dokumentech není, má říct, že ji nezná.

**„Kde jsou naše data? Posílá se to někam?"**
> Vyhledávání běží **lokálně na tomto počítači**. Ven jde text jen v okamžiku, kdy si vyžádáte AI odpověď, a jen tehdy, pokud je AI zapnutá.

**„Musíme dokumenty nějak připravovat?"**
> Ne. Vložíte název a text, kliknete uložit — o „pochopení" se aplikace postará sama.

**„Zvládne to hodně dokumentů?"**
> Ano. Databáze je stavěná na rychlé hledání i mezi velkým množstvím dokumentů.

---

## 9. Slovníček (kdyby padl odborný termín)

| Odborný pojem | Co říct místo něj |
|---|---|
| Embedding / vektor | „souřadnice na mapě významů" |
| Sémantické vyhledávání | „hledání podle významu, ne podle slov" |
| RAG | „nejdřív najdi v dokumentech, pak z nich nech AI odpovědět" |
| Claude / LLM | „umělá inteligence, která umí psát text" |
| pgvector / PostgreSQL | „databáze, která umí měřit vzdálenost mezi významy" |
| Python / FastAPI | „programovací jazyk a nástroj, ve kterých je to postavené" |
| Docker | „zabalení aplikace tak, aby běžela všude stejně" |

---

## 10. Shrnutí na jeden dech (na závěr prezentace)

> „Nasypete sem svoje dokumenty. Ptáte se **lidsky**. Aplikace najde, **co se ptáte podle významu**, a AI vám z toho napíše **odpověď se zdrojem** — aniž by si vymýšlela. A všechno to hlavní běží **u vás na počítači**."
