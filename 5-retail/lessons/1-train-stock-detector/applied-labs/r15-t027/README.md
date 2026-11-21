# Applied Lab: Bounding-box Intersection over Union (IoU)

Coursework Task: **R15-T027**
Context Lesson: `5-retail/lessons/1-train-stock-detector`

---

## 1. Learning Objective

In object detection (such as training stock detectors to count products on retail store shelves), models predict bounding boxes around items. Intersection over Union (IoU) measures how much a predicted box overlaps a reference box. It is also used by techniques such as Non-Maximum Suppression (NMS), which helps eliminate duplicate overlapping predictions.

The objective of this lab is to implement a robust, verified, and testable geometric calculation of axis-aligned 2D bounding-box IoU in pure Python standard library.

---

## 2. Coordinate Convention

All bounding boxes in this lab use the standard 4-element coordinate representation:

```text
[x_min, y_min, x_max, y_max]
```

- `x_min`: Left edge horizontal coordinate.
- `y_min`: Top edge vertical coordinate.
- `x_max`: Right edge horizontal coordinate.
- `y_max`: Bottom edge vertical coordinate.
- **Orientation**: $x$ increases from left to right; $y$ increases from top to bottom (standard computer graphics & digital image coordinate space).
- Coordinates represent numeric pixel-like values.
- Inverted boxes (where $x_{\min} > x_{\max}$ or $y_{\min} > y_{\max}$) are strictly rejected with `ValueError` and never silently reordered.
- Degenerate zero-width or zero-height boxes ($x_{\min} = x_{\max}$ or $y_{\min} = y_{\max}$) are permitted; their individual area is $0.0$, and when the total union area is $0.0$, IoU evaluates to $0.0$.

---

## 3. Mathematical Formula & Worked Calculation

Intersection over Union is defined as the ratio between the area of overlap (intersection) and the area of enclosure (union):

$$\text{IoU} = \frac{\text{Area}(\text{Box}_A \cap \text{Box}_B)}{\text{Area}(\text{Box}_A \cup \text{Box}_B)} = \frac{\text{Area}(\text{Intersection})}{\text{Area}(A) + \text{Area}(B) - \text{Area}(\text{Intersection})}$$

### Algorithm Steps:
1. **Individual Areas**:
   $$\text{Area}_A = (x_{\max}^A - x_{\min}^A) \times (y_{\max}^A - y_{\min}^A)$$
   $$\text{Area}_B = (x_{\max}^B - x_{\min}^B) \times (y_{\max}^B - y_{\min}^B)$$
2. **Intersection Bounding Box**:
   $$x_{\min}^{\cap} = \max(x_{\min}^A, x_{\min}^B), \quad y_{\min}^{\cap} = \max(y_{\min}^A, y_{\min}^B)$$
   $$x_{\max}^{\cap} = \min(x_{\max}^A, x_{\max}^B), \quad y_{\max}^{\cap} = \min(y_{\max}^A, y_{\max}^B)$$
3. **Clamped Dimensions**:
   $$W_{\cap} = \max(0.0, x_{\max}^{\cap} - x_{\min}^{\cap}), \quad H_{\cap} = \max(0.0, y_{\max}^{\cap} - y_{\min}^{\cap})$$
   $$\text{Area}(\text{Intersection}) = W_{\cap} \times H_{\cap}$$
4. **Union Area**:
   $$\text{Area}(\text{Union}) = \text{Area}_A + \text{Area}_B - \text{Area}(\text{Intersection})$$
5. **IoU Quotient**:
   $$\text{IoU} = \begin{cases} \frac{\text{Area}(\text{Intersection})}{\text{Area}(\text{Union})} & \text{if } \text{Area}(\text{Union}) > 0 \\ 0.0 & \text{if } \text{Area}(\text{Union}) = 0 \end{cases}$$

---

## 4. Mandatory Worked Fixture

Consider two overlapping square bounding boxes:

- **Box A**: `[0, 0, 2, 2]`
- **Box B**: `[1, 1, 3, 3]`

### Calculation:
- $\text{Width}_A = 2 - 0 = 2$, $\text{Height}_A = 2 - 0 = 2 \implies \text{Area}_A = 4.0$
- $\text{Width}_B = 3 - 1 = 2$, $\text{Height}_B = 3 - 1 = 2 \implies \text{Area}_B = 4.0$
- **Intersection**:
  - $x_{\min}^{\cap} = \max(0, 1) = 1$
  - $y_{\min}^{\cap} = \max(0, 1) = 1$
  - $x_{\max}^{\cap} = \min(2, 3) = 2$
  - $y_{\max}^{\cap} = \min(2, 3) = 2$
  - $W_{\cap} = 2 - 1 = 1$, $H_{\cap} = 2 - 1 = 1 \implies \text{Area}(\text{Intersection}) = 1.0$
- **Union**:
  $$\text{Area}(\text{Union}) = 4.0 + 4.0 - 1.0 = 7.0$$
- **IoU**:
  $$\text{IoU} = \frac{1.0}{7.0} = \frac{1}{7} \approx 0.142857142857\dots$$

### Additional Scenarios:
- **Identical Boxes**: Two identical boxes share 100% overlap, yielding $\text{IoU} = 1.0$.
- **Disjoint Boxes**: Non-overlapping boxes yield $\text{Area}(\text{Intersection}) = 0.0 \implies \text{IoU} = 0.0$.
- **Touching Boxes**: Boxes touching along an edge or vertex have $W_{\cap} = 0$ or $H_{\cap} = 0$, giving $\text{IoU} = 0.0$.

---

## 5. How to Run the Example and CLI Scenarios

The script `example.py` provides three execution modes:

### Default / Normal Scenario
Runs the mandatory worked fixture and core demonstrations:
```bash
python3 5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027/example.py
# Or explicitly:
python3 5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027/example.py normal
```

### Boundary Scenario
Demonstrates edge-touching boxes (horizontal, vertical, corner) and zero-area degenerate cases:
```bash
python3 5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027/example.py boundary
```

### Failure Scenario
Deliberately executes an incorrect assertion to demonstrate that verification checks fail non-zero:
```bash
python3 5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027/example.py failure
```
*(Exits with status code `1` via an uncaught AssertionError)*

---

## 6. How to Run Unit Tests

Execute test discovery using the Python 3 standard library `unittest` module:

```bash
python3 -m unittest discover -s 5-retail/lessons/1-train-stock-detector/applied-labs/r15-t027 -p "test_*.py" -v
```

---

## 7. Prerequisites and Technical Scope

- **Prerequisites**: Python 3.8+ (standard library only, no external pip dependencies).
- **Scope & Limitations**:
  - This is a local 2D planar geometry simulation using numeric coordinate arrays.
  - It does **not** load or decode images, train or run neural network object detectors (e.g. YOLO, Faster R-CNN), call Azure Custom Vision APIs, or make real-time retail detection claims.
