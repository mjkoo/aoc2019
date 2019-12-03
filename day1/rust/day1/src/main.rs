use std::env;
use std::fs::File;
use std::io::{BufRead, BufReader};

fn calc_fuel(mass: i64) -> i64 {
    mass / 3 - 2
}

fn total_fuel(mass: i64) -> i64 {
    let additional_fuel = calc_fuel(mass);
    if additional_fuel > 0 {
        additional_fuel + total_fuel(additional_fuel)
    } else {
        mass
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let filename = args.get(1).expect("No file specified");
    let file = File::open(filename).expect("Could not open input file");
    let reader = BufReader::new(file);

    let mut part_1_fuel = 0i64;
    let mut part_2_fuel = 0i64;
    for line in reader.lines() {
        let line = line.expect("Error reading line");
        let mass: i64 = line.parse().expect("Invalid input format");
        part_1_fuel += calc_fuel(mass);
        part_2_fuel += total_fuel(mass);
    }

    println!("{}", part_1_fuel);
    println!("{}", part_2_fuel);
}
