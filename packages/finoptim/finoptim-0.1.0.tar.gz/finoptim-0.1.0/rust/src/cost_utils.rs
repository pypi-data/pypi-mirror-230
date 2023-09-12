#![warn(unused_assignments)]


use ndarray::Zip;
use ndarray::prelude::*;

use crate::pricing_models::{Term, PricingModel};




pub fn cost_scalar(
    usage: ArrayView2<f64>,
    prices: ArrayView2<f64>,
    levels: ArrayView1<f64>,
    dump: &mut Array2<f64>) -> f64 {
        // deprecated function
        // do not use
    let od_price = prices.slice(s![0, ..]);
    let sp_price = prices.slice(s![1, ..]);
    let ri_price = prices.slice(s![2, ..]);
    let reservations = levels.slice(s![1..]);
    let s = levels[0];
    let timespan = usage.nrows();

    let mut cost = (&reservations * &ri_price).sum() + s;
    cost *= 24. * timespan as f64;
    
    *dump = &usage - &reservations;
    (*dump).mapv_inplace(|d| if d < 0. {0.} else {d});
    
    let mut s: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 1]>> = Array::ones(timespan) * s * 24.;
    for i in 0..usage.ncols() {
        let savings_plans_hours = &s / sp_price[i];
        let mut col_i: ArrayBase<ndarray::ViewRepr<&mut f64>, Dim<[usize; 1]>> = (*dump).column_mut(i);
        let mut min = col_i.to_owned();
        Zip::from(&mut min).and(&savings_plans_hours).for_each(|z, &y| {*z = z.min(y)});

        col_i -= &min;
        min *= sp_price[i];
        s -= &min;
    };

    *dump *= &od_price;

    cost + dump.sum()
}



pub fn cost(
    usage: ArrayView2<f64>,
    prices: ArrayView2<f64>,
    levels: ArrayView2<f64>,
    dump: &mut Array2<f64>)
     -> f64 {
    let od_price = prices.slice(s![0, ..]);
    let sp_price = prices.slice(s![1, ..]);
    let ri_price = prices.slice(s![2, ..]);
    let reservations = levels.slice(s![.., 1..]);
    let mut s = levels.slice(s![.., 0]).to_owned();

    let cost = (&reservations * &ri_price).sum() + s.sum();
    
    *dump = &usage - &reservations;
    (*dump).mapv_inplace(|d| if d < 0. {0.} else {d});
    
    for i in 0..usage.ncols() {
        let savings_plans_hours = &s / sp_price[i];
        let mut col_i: ArrayBase<ndarray::ViewRepr<&mut f64>, Dim<[usize; 1]>> = (*dump).column_mut(i);
        let mut min = col_i.to_owned();
        Zip::from(&mut min).and(&savings_plans_hours).for_each(|z, &y| {*z = z.min(y)});
        col_i -= &min;
        min *= sp_price[i];
        s -= &min;
    };
    *dump *= &od_price;

    cost + dump.sum()
}

pub fn coverage(
    usage: ArrayView2<f64>,
    prices: ArrayView2<f64>,
    levels: ArrayView2<f64>)
    -> f64 {


    let od_price = prices.slice(s![0, ..]);
    let sp_price = prices.slice(s![1, ..]);
    
    let reservations = levels.slice(s![.., 1..]);
    let mut s = levels.slice(s![.., 0]).to_owned();

    let num = (&usage * &od_price).sum();
    let mut denum = reservations.sum_axis(Axis(0));
    
    let mut col_i = usage.column(0).to_owned();

    for i in 0..usage.ncols() {
        let savings_plans_hours = &s / sp_price[i];
        col_i = 0. + &usage.column(i);
        let mut min = col_i.to_owned();
        Zip::from(&mut min).and(&savings_plans_hours).for_each(|z, &y| {*z = z.min(y)});

        denum[i] += min.sum(); // hours of savings plans used
        min *= sp_price[i];
        s -= &min;
    };

    ((denum * od_price).sum() + s.sum()) / num
    // (denum * od_price).sum() / num

}


pub fn underutilisation(usage: ArrayView2<f64>, prices: ArrayView2<f64>, levels: ArrayView1<f64>, dump: &mut Array2<f64>) -> f64 {
    let sp_price = prices.slice(s![1, ..]);
    let ri_price = prices.slice(s![2, ..]);
    let reservations = levels.slice(s![1..]);
    let s = levels[0];
    let timespan = usage.nrows();

    let mut underutilisation = 0.;
    
    *dump = &usage - &reservations;
    underutilisation += ((*dump).mapv(|d| if d < 0. {-d} else {0.}) * ri_price).sum();
    (*dump).mapv_inplace(|d| if d < 0. {0.} else {d});
    
    let mut s: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 1]>> = Array::ones(timespan) * s * 24.;
    for i in 0..usage.ncols() {
        let savings_plans_hours = &s / sp_price[i];
        let mut col_i: ArrayBase<ndarray::ViewRepr<&mut f64>, Dim<[usize; 1]>> = (*dump).column_mut(i);
        let mut min = col_i.to_owned();
        Zip::from(&mut min).and(&savings_plans_hours).for_each(|z, &y| {*z = z.min(y)});

        col_i -= &min;
        min *= sp_price[i];
        s -= &min;
    };

    underutilisation + s.sum()
}



pub fn cost_final(
    usage: ArrayView2<f64>,
    models: &Vec<PricingModel>,
    x: ArrayView1<f64>,
    days: bool,
    dump: &mut Array2<f64>)-> f64  {

    let (timespan, n) = usage.dim();
    let mut cost = Array1::zeros(timespan);
    let mut j = 0;

    (*dump).assign(&usage);

    for model in models.iter() {
        match model {
            PricingModel::Reservations(term, prices, curent_levels) => {
                let mut max_duration = if *term == Term::OneYear {365} else {1095};
                let levels = x.slice(s![j..j+n]);
                // substract the reservations to the usage and add them to the cost vector
                let mut reservations = curent_levels + &levels;
                if days {reservations *= 24.;} else {max_duration *= 24;}
                let mut unvalid_res = reservations.slice_mut(s![max_duration.min(timespan).., ..]);
                unvalid_res *= 0.;
                cost += &(&reservations * prices).sum_axis(Axis(1));
                *dump -= &reservations;
                (*dump).mapv_inplace(|d| if d < 0. {0.} else {d}); // find a way to only make this once if there are two RI fields
                j += n;
            },
            PricingModel::SavingsPlans(term, prices, curent_levels) => {
                let mut max_duration = if *term == Term::OneYear {365} else {1095};
                let level = x[j];
                if !days {max_duration *= 24;}
                let mut s = curent_levels + level;
                let mut unvalid_sp = s.slice_mut(s![max_duration.min(timespan)..]);
                unvalid_sp *= 0.;
                cost += &s;
                for i in 0..usage.ncols() {
                    let savings_plans_hours = &s / prices[i];
                    let mut col_i: ArrayBase<ndarray::ViewRepr<&mut f64>, Dim<[usize; 1]>> = (*dump).column_mut(i);
                    let mut min = col_i.to_owned();
                    Zip::from(&mut min).and(&savings_plans_hours).for_each(|z, &y| {*z = z.min(y)});
                    col_i -= &min; // remove used SP here
                    min *= prices[i];
                    s -= &min;
                };
                j += 1;
            },
            PricingModel::OnDemand(od_price) => {
                *dump *= od_price;
                // println!("od cost {}", (*dump).sum());
                cost += &dump.sum_axis(Axis(1));
            }
        }
    }
    cost.sum()
}


pub fn final_coverage(
    usage: ArrayView2<f64>,
    models: &Vec<PricingModel>,
    x: ArrayView1<f64>,
    days: bool,
    dump: &mut Array2<f64>) -> f64  {

    let (timespan, n) = usage.dim();
    let mut cost = Array1::zeros(timespan);

    let mut denum = 0.;
    let mut num = Array1::zeros(timespan);
    let mut unused_sp = 0.;
    let mut j = 0;

    for model in models.iter() {
        match model {
            PricingModel::Reservations(term, prices, levels) => {
                let mut max_duration = if *term == Term::OneYear {365} else {1095};
                // substract the reservations to the usage and add them to the cost vector
                let mut reservations = levels + &x.slice(s![j..j+n]);
                if days {reservations *= 24.;} else {max_duration *= 24;}
                let mut unvalid_res = reservations.slice_mut(s![max_duration.min(timespan).., ..]);
                unvalid_res *= 0.;

                num = reservations.sum_axis(Axis(0));

                *dump = &usage - &reservations;
                (*dump).mapv_inplace(|d| if d < 0. {0.} else {d}); // find a way to only make this once if there are two RI fields
                j += n;
            },
            PricingModel::SavingsPlans(term, prices, level) => {
                let mut max_duration = if *term == Term::OneYear {365} else {1095};
                if !days {max_duration *= 24;}
                let mut s = level.to_owned() + x[j];
                let mut unvalid_sp = s.slice_mut(s![max_duration.min(timespan)..]);
                unvalid_sp *= 0.;
                cost += &s;
                for i in 0..usage.ncols() {
                    let savings_plans_hours = &s / prices[i];
                    let mut col_i: ArrayBase<ndarray::ViewRepr<&mut f64>, Dim<[usize; 1]>> = (*dump).column_mut(i);
                    let mut min = col_i.to_owned();
                    Zip::from(&mut min).and(&savings_plans_hours).for_each(|z, &y| {*z = z.min(y)});
                    col_i -= &min;
                    num[i] += min.sum();
                    min *= prices[i];
                    s -= &min;
                };
                unused_sp += s.sum();

                j += 1;
            },
            PricingModel::OnDemand(od_prices) => {
                denum = (&usage * od_prices).sum();
                num *= od_prices;
            }
        }
    }

    (num.sum() + unused_sp) / denum
}


pub fn cost_final_gradient(
    usage: ArrayView2<f64>,
    steps: ArrayView1<f64>,
    x: ArrayView1<f64>,
    models: &Vec<PricingModel>,
    days: bool,
    dump: &mut Array2<f64>)-> Array1<f64>  {

        let (timespan, n) = usage.dim();

        // compute cost a first time here, and construct the following tables:

        // A: usage - 3yreservations
        // B: A - 1yreservations
        // C: B - 3ysp
        // U3: unused 3ysp
        // D: C - 1ysp
        // U1: unused 1ysp

        let j = x.len();
        let mut grad = Array1::zeros(j);
        let mut fixed_costs = Array1::zeros(j);
        let mut left_cost = Array2::zeros((timespan, n));

        let mut reservations_tables = Vec::with_capacity(2);
        let mut savings_plans_tables = Vec::with_capacity(2);

        (*dump).assign(&usage);

        // let mut cost = Array1::zeros(n);
        let mut i = 0;
        
        for model in models.iter() {
            match model {
                PricingModel::Reservations(term, prices, current_levels) => {
                    let mut max_duration = if *term == Term::OneYear {365} else {1095};
                    // substract the reservations to the usage and add them to the cost vector
                    let mut reservations = current_levels + &x.slice(s![i..i+n]);
                    if days {reservations *= 24.;} else {max_duration *= 24;}
                    max_duration = timespan.min(max_duration);
                    let mut unvalid_res = reservations.slice_mut(s![max_duration.., ..]);
                    unvalid_res *= 0.;
    
                    fixed_costs.slice_mut(s![i..i+n]).assign(&((reservations.sum_axis(Axis(0)) + &steps.slice(s![i..i+n]) * max_duration as f64).sum_axis(Axis(0)) * prices));

                    *dump -= &reservations;
                    (*dump).mapv_inplace(|d| if d < 0. {0.} else {d});
                    reservations_tables.push((*dump).clone());
                    i += n;
                },
                PricingModel::SavingsPlans(term, prices, current_level) => {
                    let mut max_duration = if *term == Term::OneYear {365} else {1095};
                    if !days {max_duration *= 24;}
                    max_duration = timespan.min(max_duration);


                    let mut s = current_level + x[i];
                    let mut ss = Array2::zeros((timespan, n));
                    let mut unvalid_sp = s.slice_mut(s![max_duration..]);

                    unvalid_sp *= 0.;
                    fixed_costs[i] = (&s + steps[i]).sum();
                    for k in 0..usage.ncols() {
                        ss.slice_mut(s![.., k]).assign(&s);

                        let savings_plans_hours = &s / prices[k];
                        let mut col_k: ArrayBase<ndarray::ViewRepr<&mut f64>, Dim<[usize; 1]>> = (*dump).column_mut(k);
                        let mut min = col_k.to_owned();
                        Zip::from(&mut min).and(&savings_plans_hours).for_each(|z, &y| {*z = z.min(y)});
                        col_k -= &min;
                        min *= prices[k];
                        s -= &min;
                    };

                    savings_plans_tables.push(ss.clone());

                    i += 1;
                },
                PricingModel::OnDemand(od_prices) => {
                    *dump *= od_prices;
                    // cost += &dump.sum_axis(Axis(0));
                    left_cost = dump.clone();
                }
            }
        }

        println!("here fixed costs : {:?}", fixed_costs);

        // here the tables are created and the cost is computed: now let's compute the grad
        grad = fixed_costs;


        for (r_index, table) in reservations_tables.iter().enumerate() {
            for k in 0..n {
                let mut right_slice = (*dump).slice_mut(s![.., k..]);
                right_slice.assign(&table.slice(s![.., k..]));
                let t = steps[r_index*n + k];
                right_slice.slice_mut(s![.., 0]).mapv_inplace(|d| if d < t {0.} else {d - t}); // here need to take into account the duration

                // compute SPs
                let mut s_index = 0;
                for m in models {
                    match m {
                        PricingModel::SavingsPlans(_, prices, _) => {
                            let mut s = savings_plans_tables[s_index].slice(s![.., k]).to_owned();
                            // right_slice has n - k columns
                            for i in 0..right_slice.ncols() {
                                let savings_plans_hours = &s / prices[i + k];
                                let mut col_i = right_slice.column_mut(i);
                                let mut min = col_i.to_owned();
                                Zip::from(&mut min).and(&savings_plans_hours).for_each(|z, &y| {*z = z.min(y)});
                                col_i -= &min;
                                min *= prices[i+k];
                                s -= &min;
                            };
                        s_index += 1;
                        },
                        PricingModel::OnDemand(od_prices) => {
                            grad[r_index*n + k] += (right_slice.sum_axis(Axis(0)) * od_prices.slice(s![k..])).sum();
                            // balek
                            // right_slice.slice_mut(s![.., 0]).assign(&table.slice(s![.., k])); // reset the first column of the slice
                            // here the left part  is correct
                            // that is : (usage - RIs - SPs) * od_prices
                            grad[r_index*n + k] += left_cost.slice(s![.., ..k]).sum();
                        },
                        _ => ()
                    }
                }
            }
        }

        // here grad for SPs

        // take the last applied reservation table
        let table = reservations_tables.last().expect("is empty if there are no reservation, we should take usage instead");

        // iterate on SPs ?
        for (index, model) in models.iter().enumerate() {
            match model {
                PricingModel::Reservations(_, _, _) => (),
                PricingModel::SavingsPlans(term, prices, current_levels) => {
                    // here need to loop again on SPs ?
                },
                PricingModel::OnDemand(od_prices) => {
                    // compute od cost
                }
            }
        }
        
        grad

    }





    // lindsay
// wassim
// hana
// friends of mathias