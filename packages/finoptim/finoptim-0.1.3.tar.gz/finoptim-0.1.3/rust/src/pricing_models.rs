use ndarray::prelude::*;
use std::cmp::Ordering;

#[derive(PartialEq, Eq, Clone, Debug)]
pub enum Term {
    ThreeYears,
    OneYear,
    AlreadyPayed,
}

#[derive(Clone, Debug)]
pub enum PricingModel<'a> {
    OnDemand(ArrayView1<'a, f64>),
    Reservations(Term, ArrayView1<'a, f64>, ArrayView2<'a, f64>),
    SavingsPlans(Term, ArrayView1<'a, f64>, ArrayView1<'a, f64>),
}

impl<'a> PricingModel<'a> {
    fn norm(&self) -> isize {
        match self {
            PricingModel::OnDemand(_) => 6,
            PricingModel::SavingsPlans(t, _, _) => match t {
                Term::AlreadyPayed => 3,
                Term::ThreeYears => 4,
                Term::OneYear => 5,
            },
            PricingModel::Reservations(t, _, _) => match t {
                Term::AlreadyPayed => 0,
                Term::ThreeYears => 1,
                Term::OneYear => 2,
            },
        }
    }
}

impl<'a> PartialOrd for PricingModel<'a> {
    fn partial_cmp(&self, other: &PricingModel) -> Option<Ordering> {
        match self.norm() - other.norm() {
            -6..=-1 => Some(Ordering::Less),
            0 => Some(Ordering::Equal),
            1..=6 => Some(Ordering::Greater),
            _ => panic!("not supposed to happend anyway"),
        }
    }
}

impl<'a> Ord for PricingModel<'a> {
    fn cmp(&self, other: &Self) -> Ordering {
        match self.norm() - other.norm() {
            -4..=-1 => Ordering::Greater,
            0 => Ordering::Equal,
            1..=4 => Ordering::Less,
            _ => panic!("not supposed to happen anyway"),
        }
    }
}

impl<'a> PartialEq for PricingModel<'a> {
    fn eq(&self, other: &Self) -> bool {
        use PricingModel::*;

        match (self, other) {
            (&OnDemand(_), &OnDemand(_)) => true,
            (&Reservations(ref a, _, _), &Reservations(ref b, _, _)) => a == b,
            (&SavingsPlans(ref a, _, _), &SavingsPlans(ref b, _, _)) => a == b,
            _ => false,
        }
    }
}

impl<'a> Eq for PricingModel<'a> {}
