# COLLATZ Interpretation

Independent research consumer of ASHES.

The initial maintained operation is the historical structural seed
interpretation `interpret_str`, defined recursively over an STR
representation.

For a rooted SHAPES form, the corresponding seed is:

    chi(Node(M)) = 1 + sum_T mult_M(T) * (chi(T) + 1)^2

The zero-child form has seed value 1.

This mapping is not the Collatz 3n+1 iteration, does not establish
the Collatz conjecture, and is not claimed to be injective.

The package depends on `agnostic-shapes-core>=4.0.0,<5.0.0`,
without a dependency on PETRA.

The initial distribution version is 0.1.0.
No release, DOI or publication is implied by these metadata.
