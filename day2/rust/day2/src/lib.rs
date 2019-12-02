macro_rules! alu { ($name: ident, $op:tt) => {
        fn $name(mem: &mut [usize], pc: usize) -> Option<usize> {
            let pa = *mem.get(pc + 1)?;
            let a = *mem.get(pa)?;

            let pb = *mem.get(pc + 2)?;
            let b = *mem.get(pb)?;

            let pres = *mem.get(pc + 3)?;
            let res = mem.get_mut(pres)?;

            *res = a $op b;
            Some(4)
        }
    };
}

alu!(add, +);
alu!(mul, *);

pub fn intcode(mem: &mut [usize]) -> Option<usize> {
    let mut pc = 0usize;
    loop {
        match mem.get(pc) {
            Some(1) => pc += add(mem, pc)?,
            Some(2) => pc += mul(mem, pc)?,
            Some(99) => break,
            _ => return None,
        }
    }

    mem.get(0).map(|p| *p)
}

pub fn init_and_run(mem: &[usize], noun: usize, verb: usize) -> Option<usize> {
    let mut mem = mem.to_vec();
    mem[1] = noun;
    mem[2] = verb;
    intcode(&mut mem)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_small() {
        let mem = &mut [1, 0, 0, 0, 99];
        assert_eq!(intcode(mem), Some(2));

        let mem = &mut [1, 1, 1, 4, 99, 5, 6, 0, 99];
        assert_eq!(intcode(mem), Some(30));

        let mem = &mut [2, 3, 0, 3, 99];
        assert_eq!(intcode(mem), Some(2));
        assert_eq!(mem[3], 6);

        let mem = &mut [2, 4, 4, 5, 99, 0];
        assert_eq!(intcode(mem), Some(2));
        assert_eq!(mem[5], 9801);
    }
}
