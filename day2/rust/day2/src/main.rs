use day2::init_and_run;
use std::env;
use std::fs;

const TARGET: usize = 19_690_720;

fn main() {
    let args: Vec<String> = env::args().collect();
    let filename = args.get(1).expect("No file specified");
    let contents = fs::read_to_string(filename).expect("Error reading file");
    let mem: Vec<usize> = contents
        .trim()
        .split(',')
        .map(|s| s.parse().expect("Invalid input format"))
        .collect();

    println!(
        "{}",
        init_and_run(&mem, 12, 2).expect("Program failed to run")
    );
    for noun in 0..100 {
        for verb in 0..100 {
            let output = init_and_run(&mem, noun, verb).expect("Program failed to run");

            if output == TARGET {
                println!("{}", 100 * noun + verb);
                return;
            }
        }
    }

    println!("No solutions found");
}
