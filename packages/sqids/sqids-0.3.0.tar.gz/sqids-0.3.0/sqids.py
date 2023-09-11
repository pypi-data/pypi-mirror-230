import sys


DEFAULT_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
DEFAULT_MIN_LENGTH = 0
DEFAULT_BLOCKLIST = [
    "0rgasm",
    "1d10t",
    "1d1ot",
    "1di0t",
    "1diot",
    "1eccacu10",
    "1eccacu1o",
    "1eccacul0",
    "1eccaculo",
    "1mbec11e",
    "1mbec1le",
    "1mbeci1e",
    "1mbecile",
    "a11upat0",
    "a11upato",
    "a1lupat0",
    "a1lupato",
    "aand",
    "ah01e",
    "ah0le",
    "aho1e",
    "ahole",
    "al1upat0",
    "al1upato",
    "allupat0",
    "allupato",
    "ana1",
    "ana1e",
    "anal",
    "anale",
    "anus",
    "arrapat0",
    "arrapato",
    "arsch",
    "arse",
    "ass",
    "b00b",
    "b00be",
    "b01ata",
    "b0ceta",
    "b0iata",
    "b0ob",
    "b0obe",
    "b0sta",
    "b1tch",
    "b1te",
    "b1tte",
    "ba1atkar",
    "balatkar",
    "bastard0",
    "bastardo",
    "batt0na",
    "battona",
    "bitch",
    "bite",
    "bitte",
    "bo0b",
    "bo0be",
    "bo1ata",
    "boceta",
    "boiata",
    "boob",
    "boobe",
    "bosta",
    "bran1age",
    "bran1er",
    "bran1ette",
    "bran1eur",
    "bran1euse",
    "branlage",
    "branler",
    "branlette",
    "branleur",
    "branleuse",
    "c0ck",
    "c0g110ne",
    "c0g11one",
    "c0g1i0ne",
    "c0g1ione",
    "c0gl10ne",
    "c0gl1one",
    "c0gli0ne",
    "c0glione",
    "c0na",
    "c0nnard",
    "c0nnasse",
    "c0nne",
    "c0u111es",
    "c0u11les",
    "c0u1l1es",
    "c0u1lles",
    "c0ui11es",
    "c0ui1les",
    "c0uil1es",
    "c0uilles",
    "c11t",
    "c11t0",
    "c11to",
    "c1it",
    "c1it0",
    "c1ito",
    "cabr0n",
    "cabra0",
    "cabrao",
    "cabron",
    "caca",
    "cacca",
    "cacete",
    "cagante",
    "cagar",
    "cagare",
    "cagna",
    "cara1h0",
    "cara1ho",
    "caracu10",
    "caracu1o",
    "caracul0",
    "caraculo",
    "caralh0",
    "caralho",
    "cazz0",
    "cazz1mma",
    "cazzata",
    "cazzimma",
    "cazzo",
    "ch00t1a",
    "ch00t1ya",
    "ch00tia",
    "ch00tiya",
    "ch0d",
    "ch0ot1a",
    "ch0ot1ya",
    "ch0otia",
    "ch0otiya",
    "ch1asse",
    "ch1avata",
    "ch1er",
    "ch1ng0",
    "ch1ngadaz0s",
    "ch1ngadazos",
    "ch1ngader1ta",
    "ch1ngaderita",
    "ch1ngar",
    "ch1ngo",
    "ch1ngues",
    "ch1nk",
    "chatte",
    "chiasse",
    "chiavata",
    "chier",
    "ching0",
    "chingadaz0s",
    "chingadazos",
    "chingader1ta",
    "chingaderita",
    "chingar",
    "chingo",
    "chingues",
    "chink",
    "cho0t1a",
    "cho0t1ya",
    "cho0tia",
    "cho0tiya",
    "chod",
    "choot1a",
    "choot1ya",
    "chootia",
    "chootiya",
    "cl1t",
    "cl1t0",
    "cl1to",
    "clit",
    "clit0",
    "clito",
    "cock",
    "cog110ne",
    "cog11one",
    "cog1i0ne",
    "cog1ione",
    "cogl10ne",
    "cogl1one",
    "cogli0ne",
    "coglione",
    "cona",
    "connard",
    "connasse",
    "conne",
    "cou111es",
    "cou11les",
    "cou1l1es",
    "cou1lles",
    "coui11es",
    "coui1les",
    "couil1es",
    "couilles",
    "cracker",
    "crap",
    "cu10",
    "cu1att0ne",
    "cu1attone",
    "cu1er0",
    "cu1ero",
    "cu1o",
    "cul0",
    "culatt0ne",
    "culattone",
    "culer0",
    "culero",
    "culo",
    "cum",
    "cunt",
    "d11d0",
    "d11do",
    "d1ck",
    "d1ld0",
    "d1ldo",
    "damn",
    "de1ch",
    "deich",
    "depp",
    "di1d0",
    "di1do",
    "dick",
    "dild0",
    "dildo",
    "dyke",
    "encu1e",
    "encule",
    "enema",
    "enf01re",
    "enf0ire",
    "enfo1re",
    "enfoire",
    "estup1d0",
    "estup1do",
    "estupid0",
    "estupido",
    "etr0n",
    "etron",
    "f0da",
    "f0der",
    "f0ttere",
    "f0tters1",
    "f0ttersi",
    "f0tze",
    "f0utre",
    "f1ca",
    "f1cker",
    "f1ga",
    "fag",
    "fica",
    "ficker",
    "figa",
    "foda",
    "foder",
    "fottere",
    "fotters1",
    "fottersi",
    "fotze",
    "foutre",
    "fr0c10",
    "fr0c1o",
    "fr0ci0",
    "fr0cio",
    "fr0sc10",
    "fr0sc1o",
    "fr0sci0",
    "fr0scio",
    "froc10",
    "froc1o",
    "froci0",
    "frocio",
    "frosc10",
    "frosc1o",
    "frosci0",
    "froscio",
    "fuck",
    "g00",
    "g0o",
    "g0u1ne",
    "g0uine",
    "gandu",
    "go0",
    "goo",
    "gou1ne",
    "gouine",
    "gr0gnasse",
    "grognasse",
    "haram1",
    "harami",
    "haramzade",
    "hund1n",
    "hundin",
    "id10t",
    "id1ot",
    "idi0t",
    "idiot",
    "imbec11e",
    "imbec1le",
    "imbeci1e",
    "imbecile",
    "j1zz",
    "jerk",
    "jizz",
    "k1ke",
    "kam1ne",
    "kamine",
    "kike",
    "leccacu10",
    "leccacu1o",
    "leccacul0",
    "leccaculo",
    "m1erda",
    "m1gn0tta",
    "m1gnotta",
    "m1nch1a",
    "m1nchia",
    "m1st",
    "mam0n",
    "mamahuev0",
    "mamahuevo",
    "mamon",
    "masturbat10n",
    "masturbat1on",
    "masturbate",
    "masturbati0n",
    "masturbation",
    "merd0s0",
    "merd0so",
    "merda",
    "merde",
    "merdos0",
    "merdoso",
    "mierda",
    "mign0tta",
    "mignotta",
    "minch1a",
    "minchia",
    "mist",
    "musch1",
    "muschi",
    "n1gger",
    "neger",
    "negr0",
    "negre",
    "negro",
    "nerch1a",
    "nerchia",
    "nigger",
    "orgasm",
    "p00p",
    "p011a",
    "p01la",
    "p0l1a",
    "p0lla",
    "p0mp1n0",
    "p0mp1no",
    "p0mpin0",
    "p0mpino",
    "p0op",
    "p0rca",
    "p0rn",
    "p0rra",
    "p0uff1asse",
    "p0uffiasse",
    "p1p1",
    "p1pi",
    "p1r1a",
    "p1rla",
    "p1sc10",
    "p1sc1o",
    "p1sci0",
    "p1scio",
    "p1sser",
    "pa11e",
    "pa1le",
    "pal1e",
    "palle",
    "pane1e1r0",
    "pane1e1ro",
    "pane1eir0",
    "pane1eiro",
    "panele1r0",
    "panele1ro",
    "paneleir0",
    "paneleiro",
    "patakha",
    "pec0r1na",
    "pec0rina",
    "pecor1na",
    "pecorina",
    "pen1s",
    "pendej0",
    "pendejo",
    "penis",
    "pip1",
    "pipi",
    "pir1a",
    "pirla",
    "pisc10",
    "pisc1o",
    "pisci0",
    "piscio",
    "pisser",
    "po0p",
    "po11a",
    "po1la",
    "pol1a",
    "polla",
    "pomp1n0",
    "pomp1no",
    "pompin0",
    "pompino",
    "poop",
    "porca",
    "porn",
    "porra",
    "pouff1asse",
    "pouffiasse",
    "pr1ck",
    "prick",
    "pussy",
    "put1za",
    "puta",
    "puta1n",
    "putain",
    "pute",
    "putiza",
    "puttana",
    "queca",
    "r0mp1ba11e",
    "r0mp1ba1le",
    "r0mp1bal1e",
    "r0mp1balle",
    "r0mpiba11e",
    "r0mpiba1le",
    "r0mpibal1e",
    "r0mpiballe",
    "rand1",
    "randi",
    "rape",
    "recch10ne",
    "recch1one",
    "recchi0ne",
    "recchione",
    "retard",
    "romp1ba11e",
    "romp1ba1le",
    "romp1bal1e",
    "romp1balle",
    "rompiba11e",
    "rompiba1le",
    "rompibal1e",
    "rompiballe",
    "ruff1an0",
    "ruff1ano",
    "ruffian0",
    "ruffiano",
    "s1ut",
    "sa10pe",
    "sa1aud",
    "sa1ope",
    "sacanagem",
    "sal0pe",
    "salaud",
    "salope",
    "saugnapf",
    "sb0rr0ne",
    "sb0rra",
    "sb0rrone",
    "sbattere",
    "sbatters1",
    "sbattersi",
    "sborr0ne",
    "sborra",
    "sborrone",
    "sc0pare",
    "sc0pata",
    "sch1ampe",
    "sche1se",
    "sche1sse",
    "scheise",
    "scheisse",
    "schlampe",
    "schwachs1nn1g",
    "schwachs1nnig",
    "schwachsinn1g",
    "schwachsinnig",
    "schwanz",
    "scopare",
    "scopata",
    "sexy",
    "sh1t",
    "shit",
    "slut",
    "sp0mp1nare",
    "sp0mpinare",
    "spomp1nare",
    "spompinare",
    "str0nz0",
    "str0nza",
    "str0nzo",
    "stronz0",
    "stronza",
    "stronzo",
    "stup1d",
    "stupid",
    "succh1am1",
    "succh1ami",
    "succhiam1",
    "succhiami",
    "sucker",
    "t0pa",
    "tapette",
    "test1c1e",
    "test1cle",
    "testic1e",
    "testicle",
    "tette",
    "topa",
    "tr01a",
    "tr0ia",
    "tr0mbare",
    "tr1ng1er",
    "tr1ngler",
    "tring1er",
    "tringler",
    "tro1a",
    "troia",
    "trombare",
    "turd",
    "twat",
    "vaffancu10",
    "vaffancu1o",
    "vaffancul0",
    "vaffanculo",
    "vag1na",
    "vagina",
    "verdammt",
    "verga",
    "w1chsen",
    "wank",
    "wichsen",
    "x0ch0ta",
    "x0chota",
    "xana",
    "xoch0ta",
    "xochota",
    "z0cc01a",
    "z0cc0la",
    "z0cco1a",
    "z0ccola",
    "z1z1",
    "z1zi",
    "ziz1",
    "zizi",
    "zocc01a",
    "zocc0la",
    "zocco1a",
    "zoccola",
]


class Sqids:
    def __init__(self, alphabet=None, min_length=None, blocklist=None):
        if alphabet is None:
            alphabet = DEFAULT_ALPHABET
        if min_length is None:
            min_length = DEFAULT_MIN_LENGTH
        if blocklist is None:
            blocklist = DEFAULT_BLOCKLIST

        for char in alphabet:
            if ord(char) > 127:
                raise ValueError("Alphabet cannot contain multibyte characters")

        if len(alphabet) < 3:
            raise ValueError("Alphabet length must be at least 3")

        if len(set(alphabet)) != len(alphabet):
            raise ValueError("Alphabet must contain unique characters")

        minLengthLimit = 255
        if (
            not isinstance(min_length, int)
            or min_length < 0
            or min_length > minLengthLimit
        ):
            raise ValueError(f"Minimum length has to be between 0 and {minLengthLimit}")

        filtered_blocklist = set()
        alphabet_chars = list(alphabet.lower())
        for word in blocklist:
            if len(word) >= 3:
                word_lower = word.lower()
                word_chars = list(word_lower)
                intersection = [c for c in word_chars if c in alphabet_chars]
                if len(intersection) == len(word_chars):
                    filtered_blocklist.add(word_lower)

        self.alphabet = self.shuffle(alphabet)
        self.min_length = min_length
        self.blocklist = filtered_blocklist

    def encode(self, numbers):
        if not numbers:
            return ""

        in_range_numbers = [n for n in numbers if 0 <= n <= sys.maxsize]
        if len(in_range_numbers) != len(numbers):
            max = sys.maxsize
            raise ValueError(f"Encoding supports numbers between 0 and {max}")

        return self.encode_numbers(numbers, 0)

    def encode_numbers(self, numbers, increment=0):
        if increment > len(self.alphabet):
            raise ValueError("Reached max attempts to re-generate the ID")

        offset = sum(
            (
                ord(self.alphabet[v % len(self.alphabet)]) + i
                for i, v in enumerate(numbers)
            ),
            start=len(numbers),
        ) % len(self.alphabet)
        offset = (offset + increment) % len(self.alphabet)
        alphabet = self.alphabet[offset:] + self.alphabet[:offset]
        prefix = alphabet[0]
        alphabet = alphabet[::-1]

        ret = [prefix]

        for i, num in enumerate(numbers):
            ret.append(self.to_id(num, alphabet[1:]))

            if i < len(numbers) - 1:
                ret.append(alphabet[0])
                alphabet = self.shuffle(alphabet)

        id = "".join(ret)

        if self.min_length > len(id):
            id += alphabet[0]

            while self.min_length - len(id) > 0:
                alphabet = self.shuffle(alphabet)
                id += alphabet[: min(self.min_length - len(id), len(alphabet))]

        if self.is_blocked_id(id):
            id = self.encode_numbers(numbers, increment + 1)

        return id

    def decode(self, id):
        ret = []

        if not id:
            return ret

        alphabet_chars = list(self.alphabet)
        if any(c not in alphabet_chars for c in id):
            return ret

        prefix = id[0]
        offset = self.alphabet.index(prefix)
        alphabet = self.alphabet[offset:] + self.alphabet[:offset]
        alphabet = alphabet[::-1]
        id = id[1:]

        while id:
            separator = alphabet[0]
            chunks = id.split(separator)
            if chunks:
                if chunks[0] == "":
                    return ret

                ret.append(self.to_number(chunks[0], alphabet[1:]))
                if len(chunks) > 1:
                    alphabet = self.shuffle(alphabet)

            id = separator.join(chunks[1:])

        return ret

    def shuffle(self, alphabet):
        chars = list(alphabet)

        i = 0
        j = len(chars) - 1
        while j > 0:
            r = (i * j + ord(chars[i]) + ord(chars[j])) % len(chars)
            chars[i], chars[r] = chars[r], chars[i]
            i += 1
            j -= 1

        return "".join(chars)

    def to_id(self, num, alphabet):
        id_str = []
        chars = list(alphabet)
        result = num

        while True:
            id_str.insert(0, chars[result % len(chars)])
            result = result // len(chars)
            if result == 0:
                break

        return "".join(id_str)

    def to_number(self, id_str, alphabet):
        chars = list(alphabet)
        return sum(
            chars.index(c) * (len(chars) ** i) for i, c in enumerate(id_str[::-1])
        )

    def is_blocked_id(self, id_str):
        id_str = id_str.lower()

        for word in self.blocklist:
            if len(word) <= len(id_str):
                if len(id_str) <= 3 or len(word) <= 3:
                    if id_str == word:
                        return True
                elif any(c.isdigit() for c in word):
                    if id_str.startswith(word) or id_str.endswith(word):
                        return True
                elif word in id_str:
                    return True

        return False
