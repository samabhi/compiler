program assignments;
var
    x, y, z : integer;

begin

    (* Example 1: Variable assignment, addition and printing out an integer *)
    x := 10;
    writeln(x);
    x := 10+50;
    writeln(x);

    (*Example 2: Division*)
    y := 5 / 2;
    writeln(y);

    (* Example 3: Multiplication *)
    y := 5 * 7;
    writeln(y);

    (* Example 4: Multiple operations, and application of PEMDAS *)
    y := (10-3)/2;
    writeln(y);

    (* Example 5 *)
    z := (3+2)*(17-2);
    writeln(z);

    (* Example 6 *)
    z := z+1;
    writeln(z);
end.
