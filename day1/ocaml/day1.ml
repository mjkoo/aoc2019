open Core

let input = In_channel.read_lines Sys.argv.(1) |> List.map ~f:Int.of_string
let part_one = input |> List.reduce ~f:( + ) |> Option.value ~default:0

let () =
    printf "%d\n" part_one
