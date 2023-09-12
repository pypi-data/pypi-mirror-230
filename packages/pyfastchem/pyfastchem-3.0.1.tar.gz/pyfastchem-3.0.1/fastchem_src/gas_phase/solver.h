/*
* This file is part of the FastChem code (https://github.com/exoclime/fastchem).
* Copyright (C) 2021 Daniel Kitzmann, Joachim Stock
*
* FastChem is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* FastChem is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You find a copy of the GNU General Public License in the main
* FastChem directory under <license.md>. If not, see
* <http://www.gnu.org/licenses/>.
*/


#ifndef _gas_phase_solver_h
#define _gas_phase_solver_h

#include <vector>
#include <iostream>
#include <string>

#include "../fastchem_constants.h"
#include "../species_struct.h"
#include "../options.h"


namespace fastchem {


//Solver class
template <class double_type>
class GasPhaseSolver{
  public:
    GasPhaseSolver(FastChemOptions<double_type>& options_)
      : options(options_)
      {}

    void intertSol(
      Element<double_type>& species,
      std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules, 
      const double_type gas_density);
    void linSol(
      Element<double_type>& species,
      std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules, 
      const double_type gas_density);
    void quadSol(
      Element<double_type>& species,
      std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules, 
      const double_type gas_density);
    void newtonSol(
      Element<double_type>& species,
      std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules, 
      const double_type gas_density,
      const bool use_alternative);

    void newtonSolElectron(
      Element<double_type>& species,
      std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules,
      const double_type gas_density);

    bool nelderMeadElectron(
      Element<double_type>& electron,
      std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules, 
      const double_type initial_solution,
      const double gas_density);

  
    bool bisection(
      Element<double_type>& species,
      std::vector<double_type>& Aj,
      const double gas_density);

    void backupSol(
      Element<double_type>& species,
      std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules, 
      const double_type gas_density);

    int order_cation = -999;
    int order_anion = -999;
   
  private:
    FastChemOptions<double_type>& options;
    
    double_type A0Coeff(
      const Element<double_type>& species, const double_type gas_density);
    double_type A1Coeff(
      const Element<double_type>& species,
      const std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules);
    double_type A2Coeff(
      const Element<double_type>& species,
      const std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules);
    double_type AmCoeff(
      const Element<double_type>& species,
      const std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules, 
      const unsigned int order);
    double_type AmCoeffAlt(
      const Element<double_type>& species,
      const std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules,
      const unsigned int order);

    double_type AmCoeffElectron(
      const Element<double_type>& electron,
      const std::vector<Element<double_type>>& elements,
      const std::vector<Molecule<double_type>>& molecules,
      const int order);
};



}
#endif
