program repeatUntilLoop;
var
   a: integer;

begin
   a := 1;

   repeat
      writeln(a);
      a := a + 1
   until a = 6;

end.