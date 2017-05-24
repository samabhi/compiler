program checkCase;

var
    a, b, c, d, f : integer;
begin
    a := 90;
    b := 80;
    c := 70;
    d := 60;
    f := 50;

    (* Case statement example*)
    case (a) of
    90 : writeln(a);
    80 : writeln(b);
    70 : writeln(c);
    60 : writeln(d);
    50 : writeln(f);
    end;
end.