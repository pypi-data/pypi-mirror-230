import json
from pathlib import Path

import pytest
from dirty_equals import HasLen, HasAttributes, IsList, IsPartialDict
from pymultirole_plugins.v1.schema import Document, DocumentList, Sentence

from pyprocessors_openai_completion.openai_completion import (
    OpenAICompletionProcessor,
    OpenAICompletionParameters,
    OpenAIModel,
    flatten_document, OpenAIFunction,
)


def test_openai_completion_basic():
    model = OpenAICompletionProcessor.get_model()
    model_class = model.construct().__class__
    assert model_class == OpenAICompletionParameters


def test_flatten_doc():
    testdir = Path(__file__).parent
    source = Path(
        testdir,
        "data/complexdoc.json",
    )
    with source.open("r") as fin:
        jdoc = json.load(fin)
        doc = Document(**jdoc)
        flatten = flatten_document(doc)
        assert flatten == IsPartialDict(
            text=doc.text,
            title=doc.title,
            metadata_foo=doc.metadata["foo"],
            altTexts_0_name=doc.altTexts[0].name,
        )


JINJA_PROMPTS = {
    "preserve_entities": """Generates several variants of the following context while preserving the given named entities. Each named entity must be between square brackets using the notation [label:entity].
    Context: {{ doc.text }}
    {%- set entities=[] -%}
    {%- for a in doc.annotations -%}
      {%- do entities.append('[' + a.label + ':' + a.text + ']') -%}
    {%- endfor %}
    Given named entities using the notation [label:entity]: {{ entities|join(', ') }}
    Output language: {{ doc.metadata['language'] }}
    Output format: bullet list""",
    "substitute_entities": """Generates several variants of the following context while substituting the given named entities by semantically similar named entities with the same label, for each variant insert the new named entities between square brackets using the notation [label:entity].
    Context: {{ doc.text }}
    {%- set entities=[] -%}
    {%- for a in doc.annotations -%}
      {%- do entities.append('[' + a.label + ':' + a.text + ']') -%}
    {%- endfor %}
    Given named entities using the notation [label:entity]: {{ entities|join(', ') }}
    Output language: {{ doc.metadata['language'] }}
    Output format: bullet list""",
}


@pytest.mark.skip(reason="Not a test")
@pytest.mark.parametrize("typed_prompt", [p for p in JINJA_PROMPTS.items()])
def test_jinja_doc(typed_prompt):
    type = typed_prompt[0]
    prompt = typed_prompt[1]
    parameters = OpenAICompletionParameters(
        model=OpenAIModel.gpt_3_5_turbo,
        max_tokens=3000,
        completion_altText=type,
        prompt=prompt,
    )
    processor = OpenAICompletionProcessor()
    testdir = Path(__file__).parent
    source = Path(
        testdir,
        "data/jinjadocs.json",
    )
    with source.open("r") as fin:
        jdocs = json.load(fin)
        docs = [Document(**jdoc) for jdoc in jdocs]
        docs = processor.process(docs, parameters)
        assert docs == HasLen(6)
        sum_file = testdir / f"data/jinjadocs_{type}.json"
        dl = DocumentList(__root__=docs)
        with sum_file.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
    # noqa: E501


def chunks(seq, size=1000):  # noqa
    return (seq[pos: pos + size] for pos in range(0, len(seq), size))


@pytest.mark.skip(reason="Not a test")
def test_semeval_docs():
    start_at = 32
    parameters = OpenAICompletionParameters(
        model=OpenAIModel.gpt_3_5_turbo,
        max_tokens=3000,
    )
    processor = OpenAICompletionProcessor()
    testdir = Path(__file__).parent
    source = Path(
        testdir,
        "data/semeval_fa_da.json",
    )
    with source.open("r") as fin:
        jdocs = json.load(fin)
        for i, chunk in enumerate(chunks(jdocs, 10)):
            if i >= start_at:
                docs = [Document(**jdoc) for jdoc in chunk]
                for type, prompt in JINJA_PROMPTS.items():
                    parameters.prompt = prompt
                    parameters.completion_altText = type
                    docs = processor.process(docs, parameters)
                    # assert docs == HasLen(6)
                    sum_file = testdir / f"data/semeval_fa_da_{type}_{i}.json"
                    dl = DocumentList(__root__=docs)
                    with sum_file.open("w") as fout:
                        print(
                            dl.json(exclude_none=True, exclude_unset=True, indent=2),
                            file=fout,
                        )


@pytest.mark.skip(reason="Not a test")
@pytest.mark.parametrize("model", [m for m in OpenAIModel])
def test_openai_prompt(model):
    parameters = OpenAICompletionParameters(
        model=model, max_tokens=120, completion_altText="completion"
    )
    processor = OpenAICompletionProcessor()
    docs_with_prompts = [
        (
            Document(
                identifier="1",
                text="séisme de magnitude 7,8 a frappé la Turquie",
                metadata={"language": "fr"},
            ),
            "Peux tu écrire un article de presse concernant: $text",
        ),
        (
            Document(
                identifier="2",
                text="j'habite dans une maison",
                metadata={"language": "fr"},
            ),
            "Peux tu me donner des phrases similaires à: $text",
        ),
        (
            Document(
                identifier="3",
                text="il est né le 21 janvier 2000",
                metadata={"language": "fr"},
            ),
            "Peux tu me donner des phrases similaires en changeant le format de date à: $text",
        ),
        (
            Document(
                identifier="4",
                text="""Un nuage de fumée juste après l’explosion, le 1er juin 2019.
                Une déflagration dans une importante usine d’explosifs du centre de la Russie a fait au moins 79 blessés samedi 1er juin.
                L’explosion a eu lieu dans l’usine Kristall à Dzerzhinsk, une ville située à environ 400 kilomètres à l’est de Moscou, dans la région de Nijni-Novgorod.
                « Il y a eu une explosion technique dans l’un des ateliers, suivie d’un incendie qui s’est propagé sur une centaine de mètres carrés », a expliqué un porte-parole des services d’urgence.
                Des images circulant sur les réseaux sociaux montraient un énorme nuage de fumée après l’explosion.
                Cinq bâtiments de l’usine et près de 180 bâtiments résidentiels ont été endommagés par l’explosion, selon les autorités municipales. Une enquête pour de potentielles violations des normes de sécurité a été ouverte.
                Fragments de shrapnel Les blessés ont été soignés après avoir été atteints par des fragments issus de l’explosion, a précisé une porte-parole des autorités sanitaires citée par Interfax.
                « Nous parlons de blessures par shrapnel d’une gravité moyenne et modérée », a-t-elle précisé.
                Selon des représentants de Kristall, cinq personnes travaillaient dans la zone où s’est produite l’explosion. Elles ont pu être évacuées en sécurité.
                Les pompiers locaux ont rapporté n’avoir aucune information sur des personnes qui se trouveraient encore dans l’usine.
                """,
                metadata={"language": "fr"},
            ),
            "Peux résumer dans un style journalistique le texte suivant: $text",
        ),
        (
            Document(
                identifier="5",
                text="Paris is the capital of France and Emmanuel Macron is the president of the French Republic.",
                metadata={"language": "en"},
            ),
            "Can you find the names of people, organizations and locations in the following text:\n\n $text",
        ),
    ]
    docs = []
    for doc, prompt in docs_with_prompts:
        parameters.prompt = prompt
        doc0 = processor.process([doc], parameters)[0]
        docs.append(doc0)
        assert doc0.altTexts == IsList(
            HasAttributes(name=parameters.completion_altText)
        )
    testdir = Path(__file__).parent / "data"
    sum_file = testdir / f"en_{model.value}.json"
    dl = DocumentList(__root__=docs)
    with sum_file.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


# noqa: E501
@pytest.mark.skip(reason="Not a test")
@pytest.mark.parametrize("model", [m for m in OpenAIModel])
def test_openai_text(model):
    parameters = OpenAICompletionParameters(
        model=model,
        max_tokens=120,
        best_of=3,
        n=3,
        completion_altText="completion",
    )
    processor = OpenAICompletionProcessor()
    docs = [
        Document(
            identifier="1",
            text="Peux tu écrire un article de presse concernant: séisme de magnitude 7,8 a frappé la Turquie",
            metadata={"language": "fr"},
        ),
        Document(
            identifier="2",
            text="Peux tu me donner des phrases similaires à: j'habite dans une maison",
            metadata={"language": "fr"},
        ),
    ]
    docs = processor.process(docs, parameters)
    assert docs == HasLen(2)
    for doc in docs:
        assert doc.altTexts == IsList(HasAttributes(name=parameters.completion_altText))
    testdir = Path(__file__).parent / "data"
    sum_file = testdir / f"fr_{model.value}.json"
    dl = DocumentList(__root__=docs)
    with sum_file.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


# noqa: E501
@pytest.mark.skip(reason="Not a test")
def test_q_and_a():
    prompt = """Répondre à la question en utilisant les segments suivants et en citant les références.
    Question: {{ doc.altTexts[0].text }}
    Segments: {{ doc.text }}"""

    parameters = OpenAICompletionParameters(
        model=OpenAIModel.gpt_3_5_turbo,
        max_tokens=2000,
        completion_altText=None,
        prompt=prompt,
    )
    processor = OpenAICompletionProcessor()
    testdir = Path(__file__).parent
    source = Path(
        testdir,
        "data/question_segments.json",
    )
    with source.open("r") as fin:
        jdoc = json.load(fin)
        docs = [Document(**jdoc)]
        docs = processor.process(docs, parameters)
        assert docs == HasLen(1)
        sum_file = testdir / "data/question_segments_answer.json"
        dl = DocumentList(__root__=docs)
        with sum_file.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
    # noqa: E501


@pytest.mark.skip(reason="Not a test")
def test_azure_endpoint():
    parameters = OpenAICompletionParameters(
        model=OpenAIModel.gpt_4,
        max_tokens=1000,
        best_of=3,
        n=3,
        completion_altText="completion",
    )
    processor = OpenAICompletionProcessor()
    docs = [
        Document(
            identifier="1",
            text="Peux tu écrire un article de presse concernant: séisme de magnitude 7,8 a frappé la Turquie",
            metadata={"language": "fr"},
        ),
        Document(
            identifier="2",
            text="Peux tu me donner des phrases similaires à: j'habite dans une maison",
            metadata={"language": "fr"},
        ),
    ]
    docs = processor.process(docs, parameters)
    assert docs == HasLen(2)
    for doc in docs:
        assert doc.altTexts == IsList(HasAttributes(name=parameters.completion_altText))
    testdir = Path(__file__).parent / "data"
    sum_file = testdir / "fr_azure_gpt_4.json"
    dl = DocumentList(__root__=docs)
    with sum_file.open("w") as fout:
        fout.write(dl.json(exclude_none=True, exclude_unset=True, indent=2))


# noqa: E501
@pytest.mark.skip(reason="Not a test")
def test_function_call():
    candidate_labels = {
        'per': 'Personne',
        'loc': 'Lieu géographique',
        'org': 'Organisation',
    }

    prompt = """Your task is to extract all occurences of named entities of the given labels in the provided text segments.
    Each text segment is prefixed by an index number followed by a closing parenthesis like 1) and postfixed by ===.
    Your response should include all identified named entities, their corresponding segment index numers, labels, and the start and end offsets in their correponding segment for each occurrence.
    {%- set labels=[] -%}
    {%- for l in parameters.candidate_labels.values() -%}
      {%- do labels.append('"' + l + '"') -%}
    {%- endfor %}
    Labels: {{ labels|join(', ') }}
    Segments:
    {%- for seg in doc.sentences %}
      {{ loop.index0 }}) {{ doc.text[seg.start:seg.end] }}
      ===
    {%- endfor %}"""

    parameters = OpenAICompletionParameters(
        model=OpenAIModel.gpt_3_5_turbo_16k_0613,
        max_tokens=14000,
        completion_altText=None,
        prompt=prompt,
        function=OpenAIFunction.add_annotations,
        candidate_labels=candidate_labels
    )
    processor = OpenAICompletionProcessor()
    docs = [
        Document(
            identifier="2",
            text="Cinq choses à savoir sur Toutankhamon et son fabuleux trésor\n\nL'ouverture, il y a 100 ans, du tombeau du pharaon égyptien Toutankhamon, l'une des plus grandes découvertes archéologiques de tous les temps, reste nimbée de mystères.\n\n\nVoici cinq choses à savoir sur l'enfant-roi, ses énigmes et ses trésors:\n\n\n- Un trésor inviolé -\n\n\nEn novembre 1922, après six saisons de fouilles infructueuses, l'archéologue britannique Howard Carter, son équipe égyptienne et le riche mécène Lord Carnarvon découvrent une sépulture inviolée dans la Vallée des Rois, près de Louxor en Haute-Egypte.\n\n\nLe trésor funéraire, réparti dans les cinq pièces du tombeau, est intact, avec 4.500 objets (mobilier, bijoux, statuettes), dont bon nombre en or massif.\n\n\nLe tombeau du jeune pharaon, mort à 19 ans aux environ de 1324 avant Jésus-Christ, est le seul mausolée de l'Egypte antique à avoir livré un tel trésor.\n\n\nLes innombrables autres tombeaux de pharaons et notables mis au jour jusqu'alors avaient été pillés au fil des millénaires.\n\n\n- Cercueil en or massif -\n\n\nParmi les objets découverts: un lit en bois plaqué or orné d'une tête de lion, un char ou encore un poignard au manche d'or, forgé à partir du fer de météorites selon des chercheurs.\n\n\nLe spectaculaire sarcophage en quartzite rouge hébergeait trois cercueils emboîtés les uns dans les autres, dont le dernier (110 kg) en or massif abritait la momie de Toutankhamon.\n\n\nMais la pièce maîtresse du trésor, devenue l'un des objets égyptiens les plus reconnaissables au monde, est un masque funéraire en or de plus de 10 kg incrusté de lapis-lazuli et d'autres pierres semi-précieuses.\n\n\n- Un arbre généalogique énigmatique -\n\n\nDes tests ont permis d'établir que le père de Toutankhamon était le pharaon Akhenaton, qui a régné entre 1351 et 1334 avant Jésus-Christ.\n\n\nAkhenaton était l'époux de la légendaire reine Néfertiti.\n\n\nPour autant, celle-ci n'est pas la mère de Toutankhamon. La mère du jeune pharaon, dont la momie a été retrouvée, serait la soeur de son père. L'analyse génétique montre en effet une consanguinité entre les parents.\n\n\nToutankhamon aurait épousé sa demi-soeur, Ankhsenpaamon. Le mariage entre frère et soeur était commun dans l'Egypte des pharaons.\n\n\nLe couple n'a pas de descendance connue mais deux momies d'enfants mort-nés ont toutefois été découvertes dans la tombe du jeune roi.\n\n\n- Un règne troublé, une mort mystérieuse -\n\n\nC'est à neuf ans, vers 1333 avant Jésus-Christ, que Toutankhamon serait monté sur le trône de Haute et Basse Egypte, mais les âges et les dates varient d'un spécialiste à l'autre.\n\n\nLe pays sort alors d'une période troublée, marquée par la volonté d'Akhenaton d'instaurer une forme de monothéisme dédiée au dieu du soleil Aton.\n\n\nL'arrivée au pouvoir du jeune prince permet aux tenants du culte d'Amon de reprendre le dessus et de rétablir les divinités traditionnelles.\n\n\nPlusieurs théories ont circulé sur les causes de son décès: maladie, accident de char ou meurtre.\n\n\nEn 2010, des tests génétiques et des études radiologiques ont révélé que l'adolescent serait en fait mort de paludisme combiné à une affection osseuse. Le jeune roi boitait d'un pied en raison d'une nécrose osseuse et son système immunitaire était déficient.\n\n\n- Un trésor maudit ? -\n\n\nQuelques mois après la fabuleuse découverte, le mythe de la malédiction du pharaon, qui frapperait ceux qui ont ouvert le tombeau, prend corps lorsque Lord Carnavon meurt en avril 1923 de septicémie, après une coupure infectée.\n\n\nLa légende se nourrit aussi d'une série de décès, comme celui de Carter qui meurt d'un cancer en 1939 à l'âge de 64 ans sans avoir achevé la publication de son ouvrage sur la sépulture, alors qu'il avait consacré dix ans à répertorier le trésor.\n\n\nAgatha Christie s'inspirera de la malédiction de Toutankhamon pour une de ses célèbres nouvelles: \"L'aventure du tombeau égyptien\".\n\n\nbur-kd-ays/mw/sbh/roc",
            sentences=[
                Sentence(start=0,
                         end=230
                         ),
                Sentence(start=233,
                         end=582
                         ),
                Sentence(start=585,
                         end=738
                         ),
                Sentence(start=741,
                         end=893
                         ),
                Sentence(start=896,
                         end=1019
                         ),
                Sentence(start=1022,
                         end=1232
                         ),
                Sentence(start=1235,
                         end=1415
                         ),
                Sentence(start=1418,
                         end=1630
                         ),
                Sentence(start=1633,
                         end=1810
                         ),
                Sentence(start=1813,
                         end=1870
                         ),
                Sentence(start=1873,
                         end=1929
                         ),
                Sentence(start=1930,
                         end=2015
                         ),
                Sentence(start=2016,
                         end=2088
                         ),
                Sentence(start=2091,
                         end=2147
                         ),
                Sentence(start=2148,
                         end=2220
                         ),
                Sentence(start=2223,
                         end=2356
                         ),
                Sentence(start=2359,
                         end=2583
                         ),
                Sentence(start=2586,
                         end=2731
                         ),
                Sentence(start=2734,
                         end=2874
                         ),
                Sentence(start=2877,
                         end=2974
                         ),
                Sentence(start=2977,
                         end=3128
                         ),
                Sentence(start=3129,
                         end=3235
                         ),
                Sentence(start=3238,
                         end=3258
                         ),
                Sentence(start=3259,
                         end=3490
                         ),
                Sentence(start=3493,
                         end=3738
                         ),
                Sentence(start=3741,
                         end=3896
                         )
            ],
            metadata={"language": "fr"},
        ),
        Document(
            identifier="1",
            text="Emmanuel Macron est le président de la France et Elizabeth Borne est la première-ministre de la France",
            sentences=[
                Sentence(
                    start=0,
                    end=102
                ),
            ],
            metadata={"language": "fr"},
        ),
    ]
    docs = processor.process(docs, parameters)
    assert docs == HasLen(2)
    doc0 = docs[0]
    for a in doc0.annotations:
        assert a.text == doc0.text[a.start:a.end]
