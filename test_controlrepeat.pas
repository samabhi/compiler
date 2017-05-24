program repeatUntilLoop;
var
   a: integer;

begin
   a := 10;
   (* Repeat- until example *)
   repeat
      a := a + 1
      writeln(a);
   until a = 20;
end.