# SHAPES → STR → PETRA, passo per passo

Questa guida è didattica e non normativa. La sola specifica normativa del core
SHAPES resta [SPEC.md](../reference/SPEC.md); le regole dell'interpretazione
PETRA sono definite separatamente in [PETRA.md](../reference/PETRA.md).
Il percorso qui illustrato usa esplicitamente la policy LRPE di PETRA.

```text
forma SHAPES → materialize → rappresentazione STR → LRPE.interpret_str → intero positivo
```

Le frecce descrivono un percorso di rappresentazione e interpretazione.
SHAPES resta indipendente da STR e da PETRA. STR è un percorso opzionale:
è ammessa anche l'interpretazione diretta con `LRPE.interpret(shape)`.

## 1. SHAPES: la forma

Una forma si può disegnare come un **albero radicato finito**, senza ordine
tra fratelli. Più precisamente, la forma identifica tutti gli alberi che
sono isomorfi preservando la radice: nomi dei nodi e disposizione nel disegno
non contano.

Ogni nodo ha un **multinsieme finito di figli**. Un multinsieme conserva il
numero di copie uguali, senza assegnare loro un ordine. Scambiare due figli
non cambia la forma; aggiungere un'altra copia di un figlio la cambia.
Un nodo senza figli è già una forma completa, non un albero vuoto.

Nel runtime, `Shape.children` è una tupla canonica che rappresenta quel
multinsieme. L'ordine della tupla serve alla rappresentazione e non introduce
un ordine intrinseco tra fratelli.

## 2. STR: la rappresentazione

STR significa *Structural Tensor Representation*. `tensor_view.materialize`
produce una rappresentazione strutturale deterministica: forme uguali
producono lo stesso valore STR canonico.

STR raccoglie i **tipi distinti di sottoforme radicate** presenti nell'albero.
A ciascun tipo assegna una coordinata locale e registra:

- `root`: la coordinata del tipo della forma completa;
- `multiplicities[i][j]`: quante copie del tipo figlio `j` ha il tipo padre `i`.

Due figli uguali condividono il tipo, ma la loro molteplicità resta registrata.
Le coordinate identificano tipi nella rappresentazione corrente, non singole
occorrenze né identità persistenti. Una rinomina simultanea delle coordinate,
delle righe, delle colonne e della radice conserva l'informazione strutturale.

Le coordinate e i conteggi sono interi usati per descrivere la struttura.
STR non assegna alla forma un significato numerico: non contiene basi prime,
regole per gli esponenti o valori PETRA.

## 3. PETRA: l'interpretazione LRPE

PETRA (*Prime Exponent Tower Recursive Algebra*) è uno strato di interpretazione
prime/esponenti sopra SHAPES. LRPE (*Local-Rank Paired-Exponent*) è la prima
policy eseguibile mantenuta; PETRA non coincide con questa sola policy.

Secondo [PETRA.md, §18](../reference/PETRA.md#18-first-maintained-interpretation-policy),
LRPE procede ricorsivamente. A ogni nodo ordina deterministicamente le classi
distinte di figli in base alla loro struttura e assegna loro i primi
`2, 3, 5, …` secondo quel rango locale. Le copie uguali condividono una base
prima. Questo rango è una scelta interpretativa e non l'ordine dei fratelli
o il numero della coordinata STR.

Per ogni classe di figli, con molteplicità `m` e valore ricorsivo LRPE `v`,
l'esponente è:

```text
pair(m, v) = 2^(m−1) · (2v−1)
```

Il valore del nodo è il prodotto delle basi prime così elevate.
Se non ci sono figli, il prodotto è vuoto e vale `1`.
`LRPE.interpret_str` applica queste regole direttamente alla STR.

## 4. Tre forme concrete

In questa guida `ZERO`, `ONE` e `TWO` sono nomi locali degli esempi, non
costanti pubbliche né valori aritmetici intrinseci delle forme.

| Nome | Forma | STR canonica: `root`; `multiplicities` | Valore sotto LRPE |
| --- | --- | --- | ---: |
| ZERO | Un nodo senza figli | `0`; `((0,),)` | 1 |
| ONE | Un nodo con un figlio ZERO | `1`; `((0, 0), (1, 0))` | 2 |
| TWO | Un nodo con due figli ZERO | `1`; `((0, 0), (2, 0))` | 4 |

Per ONE e TWO, la coordinata `0` descrive il tipo ZERO e la coordinata `1`
il tipo della forma completa. La riga di ZERO è nulla perché non ha figli.

**ZERO:** non ha classi di figli; LRPE assegna il prodotto vuoto, `1`.

**ONE:** ha una sola classe di figli, ZERO, con `m=1` e `v=1`.
La classe ha rango locale `1`, quindi base `2`:
`pair(1, 1)=1` e il valore è `2^1=2`.

**TWO:** ha ancora una sola classe di figli, ZERO, ma con `m=2`.
STR registra quel `2` come conteggio strutturale. È poi la regola aritmetica
LRPE a trasformare `(m, v)=(2, 1)` nell'esponente
`pair(2, 1)=2^(2−1)·(2·1−1)=2`. La base è ancora `2`, quindi `2^2=4`.
Le due copie non ricevono due primi distinti: condividono la stessa classe.

La sequenza `1, 2, 4` **non è una regola generale di raddoppio**.
Già un nodo con tre figli ZERO ha esponente `pair(3, 1)=4` e valore
`2^4=16`, anziché `8`. La struttura dei figli, le loro molteplicità e
i loro valori ricorsivi determinano il calcolo LRPE.

## 5. Esempio Python eseguibile

Dalla radice del repository, salva il codice seguente in un file Python ed
eseguilo con `.venv/bin/python percorso/al/file.py`, usando l'ambiente del
progetto. Gli import e le operazioni usano esclusivamente API pubbliche.

```python
from shapes import Shape
from tensor_view import materialize
from petra import LRPE

ZERO = Shape()
ONE = Shape(children=(ZERO,))
TWO = Shape(children=(ZERO, ZERO))

for name, shape, expected in (
    ("ZERO", ZERO, 1),
    ("ONE", ONE, 2),
    ("TWO", TWO, 4),
):
    representation = materialize(shape)
    value = LRPE.interpret_str(representation)
    assert value == expected
    assert value == LRPE.interpret(shape)
    print(f"{name}: {value}")
```

Output atteso:

```text
ZERO: 1
ONE: 2
TWO: 4
```

Riutilizzare l'oggetto `ZERO` due volte conserva due incidenze figlie in TWO.
La **forma** è l'albero senza ordine tra fratelli; la **rappresentazione** STR
ne registra tipi e molteplicità; l'**interpretazione** LRPE gli assegna un
intero positivo secondo una policy esplicita.

L'API STR di LRPE è coperta dai test M3 in
[test_petra_lrpe.py](../../tests/test_petra_lrpe.py). Il gate M4 in
[test_petra_str_equivalence.py](../../tests/test_petra_str_equivalence.py)
confronta il percorso diretto e quello via STR su tutte le 3047 forme fino
a 11 nodi, anche con limiti di materializzazione. Questo controllo finito
corrobora il runtime; la fattorizzazione generale di LRPE attraverso STR è
documentata separatamente nel contratto PETRA e nell'
[ADR 0001](../architecture/0001-str-lambda-interpretation-boundary.md).
