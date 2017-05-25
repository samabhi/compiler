program arrays;

var
    n: array [1..20] of integer;
var
    i sum: integer;
var
    average : real;

begin
    sum := 0;

    for i := 1 to 20 do
    begin
        n[ i ] := i;

        sum := sum + n[ i ];
    end;

    average := sum / 20.0;
    writeln(average);
end.