program checkCase;

var
    a, b, c, d, f : integer;
begin
    a := 1;
    b := 2;
    c := 3;
    d := 4;
    f := 5;

    (* Case statement example*)
    case (a) of
    1 : writeln(a);
    2 : writeln(b);
    3 : writeln(c);
    4 : writeln(d);
    5 : writeln(f);
    end;
end.