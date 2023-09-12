#![warn(unused_assignments)]
#![warn(confusable_idents)]


// use std::sync::{Arc, Mutex};
use std::{ops::Div, cmp::Ordering};

use ndarray::Axis;
use ndarray_stats::QuantileExt;
use numpy::{IntoPyArray, PyArray1};
use pyo3::prelude::*;
use ndarray::prelude::*;
use ndarray::parallel::prelude::*;
// use pyo3::ffi::PyErr_CheckSignals;

use argminmax::ArgMinMax;

use crate::cost_utils::{coverage, underutilisation, cost_scalar};
use crate::Convergence;


pub trait Optimisable {
    fn call(&mut self, x: ArrayView1<f64>) -> f64 {0.}

    fn gradient(&mut self, x: ArrayView1<f64>) -> Array1<f64> {Array1::zeros(x.len())}

    fn cost_variations(&mut self, x: ArrayView1<f64>) -> Array1<f64> {Array1::zeros(x.len())}

    fn record(&mut self, x: ArrayView1<f64>, c: f64, speed: Option<f64>) {}

    fn should_record(&self) -> bool {false}

    fn dump_records(&self) -> Convergence {Convergence::default()}

}


#[pyclass(unsendable, frozen)]
#[derive(Clone)]
pub struct Results {
    pub argmin: Array1<usize>,
    #[pyo3(get)]
    pub n_iter: usize,
    #[pyo3(get)]
    pub minimum: f64,
    #[pyo3(get)]
    pub convergence: Convergence
}

impl Ord for Results {
    fn cmp(&self, other: &Self) -> Ordering {
        match self.minimum < other.minimum {
            true => Ordering::Less,
            false => if self.minimum == other.minimum {Ordering::Equal} else {Ordering::Greater}
        }
    }
}

impl PartialOrd for Results {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for Results {
    fn eq(&self, other: &Self) -> bool {
        self.minimum == other.minimum
    }
}

impl Eq for Results { }

#[pymethods]
impl Results {
    #[getter]
    fn argmin<'py>(&self,  py: Python<'py>) -> &'py PyArray1<usize> {
        self.argmin.clone().into_pyarray(py)
        // currently there's a copy here everytime Python wants to read this array
        // really not great
    }
}


fn l2_norm(x: ArrayView1<f64>) -> f64 {
    x.dot(&x).sqrt()
}



fn rounding<T: FnMut(ArrayView1<f64>)->f64>(
        function: &mut T,
        point: ArrayView1<f64>) -> Array1<usize> {

    let mut x = point.to_owned();
    let n = point.len();

    let h: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 2]>> = Array2::from_diag(&Array1::ones(n));
    
    let mut grad = |x: ArrayView1<f64>| {
        let mut tmp = &h + &x;
        let c = function(x);
        tmp.map_axis_mut(Axis(1), |row| {
            function(row.view()) - c
        })
    };
    
    let cost_variations = grad(point.view());
    
    let mut indices = (0..n).collect::<Vec<_>>();
    indices.sort_by(|&a, &b| cost_variations[a].partial_cmp(&cost_variations[b]).expect("never empty"));
    indices.reverse();

    drop(grad);

    for i in indices {
        x[i] = x[i].floor();
        let cost_floor: f64 = function(x.view());
        x[i] += 1.;
        let cost_ceiling: f64 = function(x.view());
        x[i] -= if cost_floor < cost_ceiling {1.} else {0.};
    };

    x.mapv(|x: f64| x as usize)               
}



pub fn inertial_optimiser<T: Optimisable>(function: &mut T,
    start: ArrayView1<f64>) -> Results {

    let n = start.len();

    let mut x = start.to_owned();
    let mut c = function.call(x.view());


    
    let mut speed =  Array::ones(n);
    // let mut cost_variations = grad(x.view());
    let mut cost_variations = Array1::zeros(x.len());

    let β = 0.96;
    let α = 0.05;
    let iter_max = 500;
    let mut n_iter = 0;
    let mut condition = true;
    let mut speed_norm: f64;

    let mut arg_min = start.to_owned();
    let mut min = function.call(start.view());

    while condition && (n_iter < iter_max) {
        n_iter += 1;

        // if n_iter % 16 == 0 {
        //     unsafe {if PyErr_CheckSignals() == -1 {panic!("Keyboard interupt");}}
        // }
            
        // println!("{n_iter}");


        // print!("{c} \r");

        // let β = 9;

        cost_variations = function.gradient(x.view());
        // println!("{:?}", cost_variations);
        speed = &speed * β - &cost_variations;
        x += &(&speed * α);
        // normaly useless
        // x.mapv_inplace(|d| if d < 0. {0.} else {d});


        speed_norm = l2_norm(speed.view());
        c = function.call(x.view());
        if function.should_record() {
            function.record(x.view(), c, Some(speed_norm));
        }
        if c < min {
            arg_min = x.clone();
            min = c;
        }
        
        condition = speed_norm > 1.;
    }
     
    let cost_variations = function.gradient(arg_min.view());
    
    let mut indices = (0..n).collect::<Vec<_>>();
    indices.sort_by(|&a, &b| cost_variations[a].partial_cmp(&cost_variations[b]).expect("never empty"));
    indices.reverse();


    for i in indices {
        arg_min[i] = arg_min[i].floor();
        let cost_floor: f64 = function.call(arg_min.view());
        arg_min[i] += 1.;
        let cost_ceiling: f64 = function.call(arg_min.view());
        arg_min[i] -= if cost_floor < cost_ceiling {1.} else {0.};
    };

             
    let arg_min = arg_min.mapv(|x: f64| x as usize);
    Results {
        argmin: arg_min.clone(),
        n_iter: n_iter,
        minimum: function.call(arg_min.mapv(|x: usize| x as f64).view()),
        convergence : function.dump_records()
    }
    
}


pub fn best_optimiser_with_details(usage: Array2<f64>, prices: Array2<f64>, step_size:f64, start: Option<Array1<f64>>) -> Results {
    let n = usage.ncols();
    let timespan = usage.nrows();
    let ri_price = prices.slice(s![2, ..]);
    let mut dump = usage.to_owned(); // malloc here
    

    let mut up: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 1]>> = Array::ones(n+1);
    let mut s =  up.slice_mut(s![1..]);
    s.assign(&s.div(&ri_price));
    up *= step_size;

    let mut levels: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 1]>> = Array::zeros(n + 1);
    let mut returned_levels: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 1]>> = Array::zeros(n + 1);
    let min_usage = usage.fold_axis(Axis(0), f64::INFINITY, |a, &x| a.min(x)) / 24.;
    let mut s: ArrayBase<ndarray::ViewRepr<&mut f64>, Dim<[usize; 1]>> = levels.slice_mut(s![1..]);
    s.assign(&min_usage);

    levels = match start {
        Some(t) => t,
        None =>  levels
    };

    let mut c = cost_scalar(usage.view(), prices.view(), levels.view(), &mut dump);

    let h: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 2]>> = Array2::from_diag(&up);
    let mut b = true;
    let mut i = 0;
    let mut cost_variations = Vec::with_capacity(n+1);
    let mut costs: Vec<f64> = Vec::new();
    let mut coverages: Vec<f64> = Vec::new();
    let mut discounts: Vec<f64> = Vec::new();
    let mut choices: Vec<usize> = Vec::new();
    let mut underutilisations: Vec<f64> = Vec::new();

    let mut j = 0;
    let mut above = 500;
    while j < above {
        i += 1;


        // print!("iteration {i}\r");
        // also it is slower than the single-threaded version 🤡
        let g = &h + &levels;
        g.axis_iter(Axis(0))
                            .into_par_iter()
                            .with_min_len(n/8)
                            .map_init(
                            || dump.clone(),
                            |init, row| cost_scalar(usage.view(), prices.view(), row.view(), init) - c)
                            .collect_into_vec(&mut cost_variations);

        // println!("new_line");
        // let mut g = &h + &levels;
        // let trucs = g.map_axis_mut(Axis(1), |row| {
        //     cost(usage.view(), prices.view(), row.view(), &mut dump) - c
        // });
        // cost_variations = trucs.to_vec();
        let (arg_min, _) =  cost_variations.argminmax();
        b = cost_variations[arg_min] < 0.;
        if !b {
            above = above.min(n / 2);
            j += 1;
        } else {
            returned_levels = levels.clone();
        }

        levels[arg_min] += up[arg_min];
        c += cost_variations[arg_min];

        costs.push(c);
        choices.push(arg_min);
        let two_dim_levels = Array2::zeros((timespan, levels.len())) + &levels;
        coverages.push(coverage(usage.view(), prices.view(), two_dim_levels.view()));
        discounts.push(cost_variations[arg_min] / (step_size * 24. * timespan as f64));
        underutilisations.push(underutilisation(usage.view(), prices.view(), levels.view(), &mut dump));

    }

    println!("done in {i} iterations !");

    let argmin = returned_levels.mapv(|x: f64| x as usize);
    Results {
        argmin: argmin.clone(),
        n_iter: i,
        minimum: cost_scalar(usage.view(), prices.view(), argmin.mapv(|x: usize| x as f64).view(), &mut dump.clone()),
        convergence : Convergence { costs: Some(costs),
                                    coverages: Some(coverages),
                                    discounts: Some(discounts),
                                    choices: Some(choices),
                                    underutilisation_cost: Some(underutilisations),
                                    speeds: None }
    }


}

pub fn best_optimiser<T: FnMut(ArrayView1<f64>)->f64>(
    function: &mut T,
    steps: ArrayView1<f64>,
    start: Array1<f64>)-> Results {

    let mut c = function(start.view());
    let n = start.len();
    let mut x = start.to_owned();

    let h: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 2]>> = Array2::from_diag(&steps);
    let mut b = true;
    let mut i = 0;
    let mut cost_variations = Vec::with_capacity(n+1);
    while b {
        i += 1;
        // print!("iteration {i}\r");

        let mut g = &h + &x;
        cost_variations = g.map_axis_mut(Axis(1), |row| {
            function(row.view()) - c
        }).to_vec();
        let (arg_min, _) =  cost_variations.argminmax();
        // println!("{}", cost_variations[arg_min]);
        b = cost_variations[arg_min] < 0.;

        if b {
            x[arg_min] += steps[arg_min];
            c += cost_variations[arg_min];
        }
    }

    println!("done in {i} iterations !");
    let argmin = rounding(function, x.view());
    Results {
        argmin: argmin.clone(),
        n_iter: i,
        minimum: function(argmin.mapv(|x: usize| x as f64).view()),
        convergence : Convergence::default()
    }
}



// fn py_inertial_optimiser<'py>(usage: PyReadonlyArray2<f64>,
//     prices: PyReadonlyArray2<f64>,
//     n_starts: Option<usize>,
//     starting_point: Option<PyReadonlyArray1<f64>>) -> Py<Results> {


// let usage = usage.as_array();
// let prices = prices.as_array();
// let n = usage.ncols();

// // each clojure here has its own memory to perform the cost computation
// // to make multiple threads, just call the factory ?
// let make_cost_function = move || {
// let mut dump = usage.to_owned();
// let (i, j) = usage.dim();
// println!("expensive copy");
// move |levels: ArrayView1<f64>| {
// let two_dim_levels = Array2::zeros((i, j  + 1)) + &levels;
// cost(usage.view(), prices.view(), two_dim_levels.view(), &mut dump)
// }
// };

// println!("starting optimiser");
// let steps = create_steps(prices.view(), 1.);


// let n_starts = match n_starts {
// Some(i) => i,
// None => 2
// };


// let res = match starting_point {
// Some(t) => inertial_optimiser(&mut make_cost_function(), steps.view(), t.as_array().view()),
// None  => {
// let space = create_space(usage.view(), prices.view(), 1.);

// let starts_vec: Vec<f64>= space.iter().map(|x| {
// let range = Uniform::from(x.clone());
// let tmp: Vec<f64> = rand::thread_rng().sample_iter(&range.clone()).take(n_starts).collect();
// tmp.into_iter()
// }).flatten().collect();


// let starts = unsafe { Array2::from_shape_vec_unchecked((n + 1, n_starts), starts_vec) };


// let mut results = Vec::with_capacity(4);
// starts.axis_iter(Axis(1))
// .into_par_iter()
// .map_init(
// make_cost_function,
// |local_cost_function, start| inertial_optimiser(local_cost_function, steps.view(), start))
// .collect_into_vec(&mut results);

// let res = results.iter().min().expect("not an empty set");

// (*res).to_owned()
// }
// };


// Python::with_gil(|py| Py::new(py, res).unwrap())
// }



pub fn default_optimiser<T: Optimisable>(function: &mut T,
    steps: ArrayView1<f64>,
    start: ArrayView1<f64>) -> Results {

    let mut c = function.call(start.view());
    let n = start.len();
    let mut x = start.to_owned();

    let mut b = true;
    let mut i = 0;
    let mut cost_variations = Array1::zeros(x.len());
    while b {
        i += 1;
        cost_variations = function.cost_variations(x.view()) - c;
        let arg_min =  cost_variations.argmin().expect("expect the costs varuations to be non empty");
        // println!("{}", cost_variations[arg_min]);
        b = cost_variations[arg_min] < 0.;

        if b {
            x[arg_min] += steps[arg_min];
            c += cost_variations[arg_min];
            if function.should_record() {
                function.record(x.view(), c, None);
            }
        }
    }

    println!("done in {i} iterations !");


    let cost_variations = function.cost_variations(x.view()) - c;
    
    let mut indices = (0..n).collect::<Vec<_>>();
    indices.sort_by(|&a, &b| cost_variations[a].partial_cmp(&cost_variations[b]).expect("never empty"));
    indices.reverse();

    for i in indices {
        x[i] = x[i].floor();
        let cost_floor: f64 = function.call(x.view());
        x[i] += 1.;
        let cost_ceiling: f64 = function.call(x.view());
        x[i] -= if cost_floor < cost_ceiling {1.} else {0.};
    };

    let argmin = x.mapv(|x: f64| x as usize);

    Results {
        argmin: argmin.clone(),
        n_iter: i,
        minimum: function.call(argmin.mapv(|x: usize| x as f64).view()),
        convergence : function.dump_records()
    }
}