program arrays;

var
    n: array [1..10] of integer;
var
    i sum: integer;
var
    average : real;

begin
    (* intialize variable *)
    sum := 0;


    for i := 1 to 10 do
    begin
        n[ i ] := i;

        (* loop through the array and calculate the sum *)
        sum := sum + n[ i ];
    end;

    (* calculate and print out the average *)
    average := sum / 10.0;
    writeln(average);
end.