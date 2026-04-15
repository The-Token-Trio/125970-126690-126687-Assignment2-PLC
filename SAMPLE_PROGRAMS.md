# Sample Programs for Parser and Interpreter

Use these examples as integration fixtures for Member 2 (parser) and Member 3 (type checker + interpreter).

## Valid Sample 1: Arithmetic + Assignment + Print

```txt
x = 10;
y = 20.5;
z = x + y * 2;
print(z);
```

## Valid Sample 2: Boolean Comparison + If/Else

```txt
x = 5;
if (x != 0) {
    print("non-zero");
} else {
    print("zero");
}
```

## Valid Sample 3: While Loop

```txt
x = 3;
while (x != 0) {
    print(x);
    x = x - 1;
}
```

## Valid Sample 4: Function Definition + Call

```txt
def add(a, b) {
    return a + b;
}

result = add(2, 3);
print(result);
```

## Valid Sample 5: Nested Expressions

```txt
x = (2 + 3) * (4 - 1);
print(x);
```

---

## Invalid Sample 1: Unterminated String (Lexer Error)

```txt
name = "hello;
print(name);
```

Expected: lexer should report unterminated string literal with line/column.

## Invalid Sample 2: Invalid Character (Lexer Error)

```txt
x = 1 @ 2;
```

Expected: lexer should reject `@`.

## Invalid Sample 3: Missing Semicolon (Parser Error)

```txt
x = 10
print(x);
```

Expected: parser should report missing `;` after assignment.

## Invalid Sample 4: Non-Boolean Condition (Type Error)

```txt
x = 5;
if (x + 1) {
    print(x);
}
```

Expected: type checker should reject non-boolean `if` condition.

## Invalid Sample 5: Type Mismatch in Assignment (Type Error)

```txt
x = 5;
x = "hello";
```

Expected: type checker should reject changing `x` from `Integer` to `String`.

