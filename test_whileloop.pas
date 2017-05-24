program whileLoop;
var
   a: integer;

begin
   a := 10;

   (* Example of while loop *)
   while  a <> 20  do
   begin
      writeln(a);
      a := a + 1;
   end;
end.