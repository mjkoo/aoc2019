use std::collections::{HashMap, HashSet};
use std::env;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::ops::{Add, AddAssign};
use std::str::FromStr;

#[derive(Debug, PartialEq)]
enum Direction {
    UP,
    DOWN,
    RIGHT,
    LEFT,
}

#[derive(Debug, PartialEq)]
struct Step {
    direction: Direction,
    distance: u64,
}

impl FromStr for Step {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let (direction, distance) = s.split_at(1);
        let direction = match direction {
            "U" => Ok(Direction::UP),
            "D" => Ok(Direction::DOWN),
            "R" => Ok(Direction::RIGHT),
            "L" => Ok(Direction::LEFT),
            _ => Err(()),
        }?;
        let distance: u64 = distance.parse().map_err(|_| ())?;

        Ok(Self {
            direction,
            distance,
        })
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
struct Point {
    x: i64,
    y: i64,
}

impl Add for Point {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        Self {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}

impl AddAssign for Point {
    fn add_assign(&mut self, other: Self) {
        *self = *self + other;
    }
}

struct Wire(HashMap<Point, u64>);

impl Wire {
    fn from_steps(steps: Vec<Step>) -> Self {
        let mut inner = HashMap::new();
        let mut pos = Point { x: 0, y: 0 };
        let mut num_steps = 0u64;

        for s in steps {
            for _ in 0..s.distance {
                num_steps += 1;
                pos += match s.direction {
                    Direction::UP => Point { x: 0, y: 1 },
                    Direction::DOWN => Point { x: 0, y: -1 },
                    Direction::RIGHT => Point { x: 1, y: 0 },
                    Direction::LEFT => Point { x: -1, y: 0 },
                };

                if !inner.contains_key(&pos) {
                    inner.insert(pos, num_steps);
                }
            }
        }

        Wire(inner)
    }

    fn points(&self) -> HashSet<Point> {
        self.0.keys().map(|p| *p).collect()
    }

    fn num_steps(&self, point: Point) -> Option<u64> {
        self.0.get(&point).map(|p| *p)
    }
}

fn find_intersections(wires: &Vec<Wire>) -> HashSet<Point> {
    let point_sets: Vec<HashSet<Point>> = wires.iter().map(|w| w.points()).collect();
    let mut iter = point_sets.iter();
    iter.next()
        .map(|ps| iter.fold(ps.clone(), |a, b| a.intersection(&b).copied().collect()))
        .unwrap_or_else(|| HashSet::new())
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let filename = args.get(1).expect("No file specified");
    let file = File::open(filename).expect("Could not open input file");
    let reader = BufReader::new(file);
    let wires: Vec<Wire> = reader
        .lines()
        .map(|line| {
            let line = line.expect("Error reading line");
            Wire::from_steps(
                line.split(',')
                    .map(|s| s.parse().expect("Invalid input format"))
                    .collect(),
            )
        })
        .collect();

    let intersections = find_intersections(&wires);
    let min_distance: u64 = intersections
        .iter()
        .map(|p| p.x.abs() as u64 + p.y.abs() as u64)
        .min()
        .expect("No interections found");
    let min_signal_delay: u64 = intersections
        .iter()
        .map(|p| wires.iter().map(|w| w.num_steps(*p).unwrap()).sum())
        .min()
        .expect("No intersections found");

    println!("{}", min_distance);
    println!("{}", min_signal_delay);
}
