function out = model
%
% qiuqiunile.m
%
% Model exported on Oct 28 2025, 23:04 by COMSOL 6.3.0.290.

import com.comsol.model.*
import com.comsol.model.util.*

model = ModelUtil.create('Model');

model.modelPath('D:\BaiduNetdiskDownload');

model.component.create('comp1', true);

model.component('comp1').geom.create('geom1', 2);

model.component('comp1').mesh.create('mesh1');

model.component('comp1').physics.create('spf', 'LaminarFlow', 'geom1');
model.component('comp1').physics.create('pf', 'PhaseField', 'geom1');

model.component('comp1').multiphysics.create('tpf1', 'TwoPhaseFlowPhaseField', 2);
model.component('comp1').multiphysics('tpf1').set('Fluid_physics', 'spf');
model.component('comp1').multiphysics('tpf1').set('Mathematics_physics', 'pf');
model.component('comp1').multiphysics('tpf1').selection.all;

model.study.create('std1');
model.study('std1').create('phasei', 'PhaseInitialization');
model.study('std1').feature('phasei').set('ftplistmethod', 'manual');
model.study('std1').feature('phasei').set('solnum', 'auto');
model.study('std1').feature('phasei').set('notsolnum', 'auto');
model.study('std1').feature('phasei').set('outputmap', {});
model.study('std1').feature('phasei').set('ngenAUX', '1');
model.study('std1').feature('phasei').set('goalngenAUX', '1');
model.study('std1').feature('phasei').set('ngenAUX', '1');
model.study('std1').feature('phasei').set('goalngenAUX', '1');
model.study('std1').feature('phasei').setSolveFor('/physics/spf', true);
model.study('std1').feature('phasei').setSolveFor('/physics/pf', true);
model.study('std1').feature('phasei').setSolveFor('/multiphysics/tpf1', true);
model.study('std1').feature('phasei').setSolveFor('/physics/spf', false);
model.study('std1').create('time', 'Transient');
model.study('std1').feature('time').set('initstudy', 'std1');
model.study('std1').feature('time').set('notstudy', 'std1');
model.study('std1').feature('time').set('ftplistmethod', 'manual');
model.study('std1').feature('time').set('initialtime', '0');
model.study('std1').feature('time').set('useinitsol', 'on');
model.study('std1').feature('time').set('notsolmethod', 'sol');
model.study('std1').feature('time').set('outputmap', {});
model.study('std1').feature('time').setSolveFor('/physics/spf', true);
model.study('std1').feature('time').setSolveFor('/physics/pf', true);
model.study('std1').feature('time').setSolveFor('/multiphysics/tpf1', true);

model.component('comp1').geom('geom1').run;
model.component('comp1').geom('geom1').create('r1', 'Rectangle');
model.component('comp1').geom('geom1').lengthUnit('mm');
model.component('comp1').geom('geom1').run;
model.component('comp1').geom('geom1').feature('r1').set('size', [1 15]);
model.component('comp1').geom('geom1').run('r1');
model.component('comp1').geom('geom1').create('arr1', 'Array');
model.component('comp1').geom('geom1').feature('arr1').selection('input').set({'r1'});
model.component('comp1').geom('geom1').feature('arr1').set('fullsize', [7 1]);
model.component('comp1').geom('geom1').feature('arr1').set('displ', [2 0]);
model.component('comp1').geom('geom1').runPre('fin');
model.component('comp1').geom('geom1').create('r2', 'Rectangle');
model.component('comp1').geom('geom1').feature('r2').set('size', [13 0.5]);
model.component('comp1').geom('geom1').feature('r2').set('pos', [0 -0.5]);
model.component('comp1').geom('geom1').runPre('fin');
model.component('comp1').geom('geom1').run('fin');

model.component('comp1').material.create('mat1', 'Common');
model.component('comp1').material('mat1').propertyGroup('def').func.create('eta', 'Piecewise');
model.component('comp1').material('mat1').propertyGroup('def').func.create('Cp', 'Piecewise');
model.component('comp1').material('mat1').propertyGroup('def').func.create('rho', 'Analytic');
model.component('comp1').material('mat1').propertyGroup('def').func.create('k', 'Piecewise');
model.component('comp1').material('mat1').propertyGroup('def').func.create('cs', 'Analytic');
model.component('comp1').material('mat1').propertyGroup('def').func.create('an1', 'Analytic');
model.component('comp1').material('mat1').propertyGroup('def').func.create('an2', 'Analytic');
model.component('comp1').material('mat1').propertyGroup.create('NonlinearModel', 'NonlinearModel', 'Nonlinear model');
model.component('comp1').material('mat1').propertyGroup.create('idealGas', 'idealGas', 'Ideal gas');
model.component('comp1').material('mat1').propertyGroup('idealGas').func.create('Cp', 'Piecewise');
model.component('comp1').material('mat1').label('Air');
model.component('comp1').material('mat1').set('family', 'air');
model.component('comp1').material('mat1').propertyGroup('def').label('Basic');
model.component('comp1').material('mat1').propertyGroup('def').func('eta').label('Piecewise');
model.component('comp1').material('mat1').propertyGroup('def').func('eta').set('arg', 'T');
model.component('comp1').material('mat1').propertyGroup('def').func('eta').set('pieces', {'200.0' '1600.0' '-8.38278E-7+8.35717342E-8*T^1-7.69429583E-11*T^2+4.6437266E-14*T^3-1.06585607E-17*T^4'});
model.component('comp1').material('mat1').propertyGroup('def').func('eta').set('argunit', 'K');
model.component('comp1').material('mat1').propertyGroup('def').func('eta').set('fununit', 'Pa*s');
model.component('comp1').material('mat1').propertyGroup('def').func('Cp').label('Piecewise 2');
model.component('comp1').material('mat1').propertyGroup('def').func('Cp').set('arg', 'T');
model.component('comp1').material('mat1').propertyGroup('def').func('Cp').set('pieces', {'200.0' '1600.0' '1047.63657-0.372589265*T^1+9.45304214E-4*T^2-6.02409443E-7*T^3+1.2858961E-10*T^4'});
model.component('comp1').material('mat1').propertyGroup('def').func('Cp').set('argunit', 'K');
model.component('comp1').material('mat1').propertyGroup('def').func('Cp').set('fununit', 'J/(kg*K)');
model.component('comp1').material('mat1').propertyGroup('def').func('rho').label('Analytic');
model.component('comp1').material('mat1').propertyGroup('def').func('rho').set('expr', 'pA*0.02897/R_const[K*mol/J]/T');
model.component('comp1').material('mat1').propertyGroup('def').func('rho').set('args', {'pA' 'T'});
model.component('comp1').material('mat1').propertyGroup('def').func('rho').set('dermethod', 'manual');
model.component('comp1').material('mat1').propertyGroup('def').func('rho').set('argders', {'pA' 'd(pA*0.02897/R_const/T,pA)'; 'T' 'd(pA*0.02897/R_const/T,T)'});
model.component('comp1').material('mat1').propertyGroup('def').func('rho').set('fununit', 'kg/m^3');
model.component('comp1').material('mat1').propertyGroup('def').func('rho').set('argunit', {'Pa' 'K'});
model.component('comp1').material('mat1').propertyGroup('def').func('rho').set('plotaxis', {'off' 'on'});
model.component('comp1').material('mat1').propertyGroup('def').func('rho').set('plotfixedvalue', {'101325' '273.15'});
model.component('comp1').material('mat1').propertyGroup('def').func('rho').set('plotargs', {'pA' '101325' '101325'; 'T' '273.15' '293.15'});
model.component('comp1').material('mat1').propertyGroup('def').func('k').label('Piecewise 3');
model.component('comp1').material('mat1').propertyGroup('def').func('k').set('arg', 'T');
model.component('comp1').material('mat1').propertyGroup('def').func('k').set('pieces', {'200.0' '1600.0' '-0.00227583562+1.15480022E-4*T^1-7.90252856E-8*T^2+4.11702505E-11*T^3-7.43864331E-15*T^4'});
model.component('comp1').material('mat1').propertyGroup('def').func('k').set('argunit', 'K');
model.component('comp1').material('mat1').propertyGroup('def').func('k').set('fununit', 'W/(m*K)');
model.component('comp1').material('mat1').propertyGroup('def').func('cs').label('Analytic 2');
model.component('comp1').material('mat1').propertyGroup('def').func('cs').set('expr', 'sqrt(1.4*R_const[K*mol/J]/0.02897*T)');
model.component('comp1').material('mat1').propertyGroup('def').func('cs').set('args', {'T'});
model.component('comp1').material('mat1').propertyGroup('def').func('cs').set('dermethod', 'manual');
model.component('comp1').material('mat1').propertyGroup('def').func('cs').set('fununit', 'm/s');
model.component('comp1').material('mat1').propertyGroup('def').func('cs').set('argunit', {'K'});
model.component('comp1').material('mat1').propertyGroup('def').func('cs').set('plotfixedvalue', {'273.15'});
model.component('comp1').material('mat1').propertyGroup('def').func('cs').set('plotargs', {'T' '273.15' '373.15'});
model.component('comp1').material('mat1').propertyGroup('def').func('an1').label('Analytic ');
model.component('comp1').material('mat1').propertyGroup('def').func('an1').set('funcname', 'alpha_p');
model.component('comp1').material('mat1').propertyGroup('def').func('an1').set('expr', '-1/rho(pA,T)*d(rho(pA,T),T)');
model.component('comp1').material('mat1').propertyGroup('def').func('an1').set('args', {'pA' 'T'});
model.component('comp1').material('mat1').propertyGroup('def').func('an1').set('fununit', '1/K');
model.component('comp1').material('mat1').propertyGroup('def').func('an1').set('argunit', {'Pa' 'K'});
model.component('comp1').material('mat1').propertyGroup('def').func('an1').set('plotaxis', {'off' 'on'});
model.component('comp1').material('mat1').propertyGroup('def').func('an1').set('plotfixedvalue', {'101325' '273.15'});
model.component('comp1').material('mat1').propertyGroup('def').func('an1').set('plotargs', {'pA' '101325' '101325'; 'T' '273.15' '373.15'});
model.component('comp1').material('mat1').propertyGroup('def').func('an2').label('Analytic 2a');
model.component('comp1').material('mat1').propertyGroup('def').func('an2').set('funcname', 'muB');
model.component('comp1').material('mat1').propertyGroup('def').func('an2').set('expr', '0.6*eta(T)');
model.component('comp1').material('mat1').propertyGroup('def').func('an2').set('args', {'T'});
model.component('comp1').material('mat1').propertyGroup('def').func('an2').set('fununit', 'Pa*s');
model.component('comp1').material('mat1').propertyGroup('def').func('an2').set('argunit', {'K'});
model.component('comp1').material('mat1').propertyGroup('def').func('an2').set('plotfixedvalue', {'200'});
model.component('comp1').material('mat1').propertyGroup('def').func('an2').set('plotargs', {'T' '200' '1600'});
model.component('comp1').material('mat1').propertyGroup('def').set('thermalexpansioncoefficient', '');
model.component('comp1').material('mat1').propertyGroup('def').set('molarmass', '');
model.component('comp1').material('mat1').propertyGroup('def').set('bulkviscosity', '');
model.component('comp1').material('mat1').propertyGroup('def').set('thermalexpansioncoefficient', {'alpha_p(pA,T)' '0' '0' '0' 'alpha_p(pA,T)' '0' '0' '0' 'alpha_p(pA,T)'});
model.component('comp1').material('mat1').propertyGroup('def').set('molarmass', '0.02897[kg/mol]');
model.component('comp1').material('mat1').propertyGroup('def').set('bulkviscosity', 'muB(T)');
model.component('comp1').material('mat1').propertyGroup('def').set('dynamicviscosity', 'eta(T)');
model.component('comp1').material('mat1').propertyGroup('def').set('ratioofspecificheat', '1.4');
model.component('comp1').material('mat1').propertyGroup('def').set('electricconductivity', {'0[S/m]' '0' '0' '0' '0[S/m]' '0' '0' '0' '0[S/m]'});
model.component('comp1').material('mat1').propertyGroup('def').set('heatcapacity', 'Cp(T)');
model.component('comp1').material('mat1').propertyGroup('def').set('density', 'rho(pA,T)');
model.component('comp1').material('mat1').propertyGroup('def').set('thermalconductivity', {'k(T)' '0' '0' '0' 'k(T)' '0' '0' '0' 'k(T)'});
model.component('comp1').material('mat1').propertyGroup('def').set('soundspeed', 'cs(T)');
model.component('comp1').material('mat1').propertyGroup('def').addInput('temperature');
model.component('comp1').material('mat1').propertyGroup('def').addInput('pressure');
model.component('comp1').material('mat1').propertyGroup('NonlinearModel').label('Nonlinear model');
model.component('comp1').material('mat1').propertyGroup('NonlinearModel').set('BA', '(def.gamma+1)/2');
model.component('comp1').material('mat1').propertyGroup('idealGas').label('Ideal gas');
model.component('comp1').material('mat1').propertyGroup('idealGas').func('Cp').label('Piecewise 2');
model.component('comp1').material('mat1').propertyGroup('idealGas').func('Cp').set('arg', 'T');
model.component('comp1').material('mat1').propertyGroup('idealGas').func('Cp').set('pieces', {'200.0' '1600.0' '1047.63657-0.372589265*T^1+9.45304214E-4*T^2-6.02409443E-7*T^3+1.2858961E-10*T^4'});
model.component('comp1').material('mat1').propertyGroup('idealGas').func('Cp').set('argunit', 'K');
model.component('comp1').material('mat1').propertyGroup('idealGas').func('Cp').set('fununit', 'J/(kg*K)');
model.component('comp1').material('mat1').propertyGroup('idealGas').set('Rs', 'R_const/Mn');
model.component('comp1').material('mat1').propertyGroup('idealGas').set('heatcapacity', 'Cp(T)');
model.component('comp1').material('mat1').propertyGroup('idealGas').set('ratioofspecificheat', '1.4');
model.component('comp1').material('mat1').propertyGroup('idealGas').set('molarmass', '0.02897[kg/mol]');
model.component('comp1').material('mat1').propertyGroup('idealGas').addInput('temperature');
model.component('comp1').material('mat1').propertyGroup('idealGas').addInput('pressure');
model.component('comp1').material('mat1').materialType('nonSolid');
model.component('comp1').material.create('mat2', 'Common');
model.component('comp1').material('mat2').propertyGroup('def').func.create('eta', 'Piecewise');
model.component('comp1').material('mat2').propertyGroup('def').func.create('Cp', 'Piecewise');
model.component('comp1').material('mat2').propertyGroup('def').func.create('rho', 'Piecewise');
model.component('comp1').material('mat2').propertyGroup('def').func.create('k', 'Piecewise');
model.component('comp1').material('mat2').propertyGroup('def').func.create('cs', 'Interpolation');
model.component('comp1').material('mat2').propertyGroup('def').func.create('an1', 'Analytic');
model.component('comp1').material('mat2').propertyGroup('def').func.create('an2', 'Analytic');
model.component('comp1').material('mat2').propertyGroup('def').func.create('an3', 'Analytic');
model.component('comp1').material('mat2').label('Water');
model.component('comp1').material('mat2').set('family', 'water');
model.component('comp1').material('mat2').propertyGroup('def').label('Basic');
model.component('comp1').material('mat2').propertyGroup('def').func('eta').label('Piecewise');
model.component('comp1').material('mat2').propertyGroup('def').func('eta').set('arg', 'T');
model.component('comp1').material('mat2').propertyGroup('def').func('eta').set('pieces', {'273.15' '413.15' '1.3799566804-0.021224019151*T^1+1.3604562827E-4*T^2-4.6454090319E-7*T^3+8.9042735735E-10*T^4-9.0790692686E-13*T^5+3.8457331488E-16*T^6'; '413.15' '553.75' '0.00401235783-2.10746715E-5*T^1+3.85772275E-8*T^2-2.39730284E-11*T^3'});
model.component('comp1').material('mat2').propertyGroup('def').func('eta').set('argunit', 'K');
model.component('comp1').material('mat2').propertyGroup('def').func('eta').set('fununit', 'Pa*s');
model.component('comp1').material('mat2').propertyGroup('def').func('Cp').label('Piecewise 2');
model.component('comp1').material('mat2').propertyGroup('def').func('Cp').set('arg', 'T');
model.component('comp1').material('mat2').propertyGroup('def').func('Cp').set('pieces', {'273.15' '553.75' '12010.1471-80.4072879*T^1+0.309866854*T^2-5.38186884E-4*T^3+3.62536437E-7*T^4'});
model.component('comp1').material('mat2').propertyGroup('def').func('Cp').set('argunit', 'K');
model.component('comp1').material('mat2').propertyGroup('def').func('Cp').set('fununit', 'J/(kg*K)');
model.component('comp1').material('mat2').propertyGroup('def').func('rho').label('Piecewise 3');
model.component('comp1').material('mat2').propertyGroup('def').func('rho').set('arg', 'T');
model.component('comp1').material('mat2').propertyGroup('def').func('rho').set('smooth', 'contd1');
model.component('comp1').material('mat2').propertyGroup('def').func('rho').set('pieces', {'273.15' '293.15' '0.000063092789034*T^3-0.060367639882855*T^2+18.9229382407066*T-950.704055329848'; '293.15' '373.15' '0.000010335053319*T^3-0.013395065634452*T^2+4.969288832655160*T+432.257114008512'});
model.component('comp1').material('mat2').propertyGroup('def').func('rho').set('argunit', 'K');
model.component('comp1').material('mat2').propertyGroup('def').func('rho').set('fununit', 'kg/m^3');
model.component('comp1').material('mat2').propertyGroup('def').func('k').label('Piecewise 4');
model.component('comp1').material('mat2').propertyGroup('def').func('k').set('arg', 'T');
model.component('comp1').material('mat2').propertyGroup('def').func('k').set('pieces', {'273.15' '553.75' '-0.869083936+0.00894880345*T^1-1.58366345E-5*T^2+7.97543259E-9*T^3'});
model.component('comp1').material('mat2').propertyGroup('def').func('k').set('argunit', 'K');
model.component('comp1').material('mat2').propertyGroup('def').func('k').set('fununit', 'W/(m*K)');
model.component('comp1').material('mat2').propertyGroup('def').func('cs').label('Interpolation');
model.component('comp1').material('mat2').propertyGroup('def').func('cs').set('table', {'273' '1403';  ...
'278' '1427';  ...
'283' '1447';  ...
'293' '1481';  ...
'303' '1507';  ...
'313' '1526';  ...
'323' '1541';  ...
'333' '1552';  ...
'343' '1555';  ...
'353' '1555';  ...
'363' '1550';  ...
'373' '1543'});
model.component('comp1').material('mat2').propertyGroup('def').func('cs').set('interp', 'piecewisecubic');
model.component('comp1').material('mat2').propertyGroup('def').func('cs').set('fununit', {'m/s'});
model.component('comp1').material('mat2').propertyGroup('def').func('cs').set('argunit', {'K'});
model.component('comp1').material('mat2').propertyGroup('def').func('an1').label('Analytic ');
model.component('comp1').material('mat2').propertyGroup('def').func('an1').set('funcname', 'alpha_p');
model.component('comp1').material('mat2').propertyGroup('def').func('an1').set('expr', '-1/rho(T)*d(rho(T),T)');
model.component('comp1').material('mat2').propertyGroup('def').func('an1').set('args', {'T'});
model.component('comp1').material('mat2').propertyGroup('def').func('an1').set('fununit', '1/K');
model.component('comp1').material('mat2').propertyGroup('def').func('an1').set('argunit', {'K'});
model.component('comp1').material('mat2').propertyGroup('def').func('an1').set('plotfixedvalue', {'273.15'});
model.component('comp1').material('mat2').propertyGroup('def').func('an1').set('plotargs', {'T' '273.15' '373.15'});
model.component('comp1').material('mat2').propertyGroup('def').func('an2').label('Analytic 2');
model.component('comp1').material('mat2').propertyGroup('def').func('an2').set('funcname', 'gamma_w');
model.component('comp1').material('mat2').propertyGroup('def').func('an2').set('expr', '1+(T/Cp(T))*(alpha_p(T)*cs(T))^2');
model.component('comp1').material('mat2').propertyGroup('def').func('an2').set('args', {'T'});
model.component('comp1').material('mat2').propertyGroup('def').func('an2').set('fununit', '1');
model.component('comp1').material('mat2').propertyGroup('def').func('an2').set('argunit', {'K'});
model.component('comp1').material('mat2').propertyGroup('def').func('an2').set('plotfixedvalue', {'273.15'});
model.component('comp1').material('mat2').propertyGroup('def').func('an2').set('plotargs', {'T' '273.15' '373.15'});
model.component('comp1').material('mat2').propertyGroup('def').func('an3').label('Analytic 3');
model.component('comp1').material('mat2').propertyGroup('def').func('an3').set('funcname', 'muB');
model.component('comp1').material('mat2').propertyGroup('def').func('an3').set('expr', '2.79*eta(T)');
model.component('comp1').material('mat2').propertyGroup('def').func('an3').set('args', {'T'});
model.component('comp1').material('mat2').propertyGroup('def').func('an3').set('fununit', 'Pa*s');
model.component('comp1').material('mat2').propertyGroup('def').func('an3').set('argunit', {'K'});
model.component('comp1').material('mat2').propertyGroup('def').func('an3').set('plotfixedvalue', {'273.15'});
model.component('comp1').material('mat2').propertyGroup('def').func('an3').set('plotargs', {'T' '273.15' '553.75'});
model.component('comp1').material('mat2').propertyGroup('def').set('thermalexpansioncoefficient', '');
model.component('comp1').material('mat2').propertyGroup('def').set('bulkviscosity', '');
model.component('comp1').material('mat2').propertyGroup('def').set('thermalexpansioncoefficient', {'alpha_p(T)' '0' '0' '0' 'alpha_p(T)' '0' '0' '0' 'alpha_p(T)'});
model.component('comp1').material('mat2').propertyGroup('def').set('bulkviscosity', 'muB(T)');
model.component('comp1').material('mat2').propertyGroup('def').set('dynamicviscosity', 'eta(T)');
model.component('comp1').material('mat2').propertyGroup('def').set('ratioofspecificheat', 'gamma_w(T)');
model.component('comp1').material('mat2').propertyGroup('def').set('electricconductivity', {'5.5e-6[S/m]' '0' '0' '0' '5.5e-6[S/m]' '0' '0' '0' '5.5e-6[S/m]'});
model.component('comp1').material('mat2').propertyGroup('def').set('heatcapacity', 'Cp(T)');
model.component('comp1').material('mat2').propertyGroup('def').set('density', 'rho(T)');
model.component('comp1').material('mat2').propertyGroup('def').set('thermalconductivity', {'k(T)' '0' '0' '0' 'k(T)' '0' '0' '0' 'k(T)'});
model.component('comp1').material('mat2').propertyGroup('def').set('soundspeed', 'cs(T)');
model.component('comp1').material('mat2').propertyGroup('def').addInput('temperature');
model.component('comp1').material('mat2').selection.set([1]);

model.component('comp1').physics('spf').create('inl1', 'InletBoundary', 1);
model.component('comp1').physics('spf').feature('inl1').selection.set([2]);
model.component('comp1').physics('spf').feature('inl1').set('ComponentWise', 'VelocityFieldComponentWise');
model.component('comp1').physics('spf').feature('inl1').set('u0', [0 0.01 0]);
model.component('comp1').physics('spf').create('out1', 'OutletBoundary', 1);
model.component('comp1').physics('spf').feature('out1').selection.set([5 10 15 20 25 30 35]);
model.component('comp1').physics('pf').feature('pfm1').set('epsilon_pf', '2e-5');
model.component('comp1').physics('pf').feature('initfluid2').selection.set([1]);
model.component('comp1').physics('pf').create('inl1', 'InletBoundary', 1);
model.component('comp1').physics('pf').feature('inl1').selection.set([2]);
model.component('comp1').physics('pf').feature('inl1').set('pfcond', 'Fluid2pf');
model.component('comp1').physics('pf').create('out1', 'Outlet', 1);
model.component('comp1').physics('pf').feature('out1').selection.set([5 10 15 20 25 30 35]);
model.component('comp1').physics('pf').create('ww2', 'WettedWall', 1);
model.component('comp1').physics('pf').feature.remove('ww2');
model.component('comp1').physics('pf').feature('ww1').set('thetaw', 'pi/6');

model.component('comp1').multiphysics('tpf1').set('Fluid1', 'mat1');
model.component('comp1').multiphysics('tpf1').set('Fluid2', 'mat2');

model.component('comp1').mesh('mesh1').create('fq1', 'FreeQuad');
model.component('comp1').mesh('mesh1').feature('size').set('custom', true);
model.component('comp1').mesh('mesh1').feature('size').set('hmax', 0.05);
model.component('comp1').mesh('mesh1').feature('size').set('hmin', 0.05);
model.component('comp1').mesh('mesh1').feature('size').set('hmax', 0.1);
model.component('comp1').mesh('mesh1').feature('size').set('hmin', 0.1);
model.component('comp1').mesh('mesh1').feature('size').set('hgrad', 1.1);
model.component('comp1').mesh('mesh1').feature('size').set('hcurve', 0.25);
model.component('comp1').mesh('mesh1').feature('fq1').selection.geom('geom1');
model.component('comp1').mesh('mesh1').run;

model.study('std1').feature('time').set('tlist', 'range(0,0.0005,0.001)');
model.study('std1').createAutoSequences('all');

model.sol('sol1').runAll;

model.result.dataset('dset1').set('geom', 'geom1');
model.result.create('pg1', 'PlotGroup2D');
model.result('pg1').label([native2unicode(hex2dec({'90' '1f'}), 'unicode')  native2unicode(hex2dec({'5e' 'a6'}), 'unicode') ' (spf)']);
model.result('pg1').set('frametype', 'spatial');
model.result('pg1').feature.create('surf1', 'Surface');
model.result('pg1').feature('surf1').label([native2unicode(hex2dec({'88' '68'}), 'unicode')  native2unicode(hex2dec({'97' '62'}), 'unicode') ]);
model.result('pg1').feature('surf1').set('showsolutionparams', 'on');
model.result('pg1').feature('surf1').set('smooth', 'internal');
model.result('pg1').feature('surf1').set('showsolutionparams', 'on');
model.result('pg1').feature('surf1').set('data', 'parent');
model.result.create('pg2', 'PlotGroup2D');
model.result('pg2').label([native2unicode(hex2dec({'53' '8b'}), 'unicode')  native2unicode(hex2dec({'52' '9b'}), 'unicode') ' (spf)']);
model.result('pg2').set('frametype', 'spatial');
model.result('pg2').feature.create('con1', 'Contour');
model.result('pg2').feature('con1').label([native2unicode(hex2dec({'7b' '49'}), 'unicode')  native2unicode(hex2dec({'50' '3c'}), 'unicode')  native2unicode(hex2dec({'7e' 'bf'}), 'unicode') ]);
model.result('pg2').feature('con1').set('showsolutionparams', 'on');
model.result('pg2').feature('con1').set('expr', 'p');
model.result('pg2').feature('con1').set('number', 40);
model.result('pg2').feature('con1').set('levelrounding', false);
model.result('pg2').feature('con1').set('smooth', 'internal');
model.result('pg2').feature('con1').set('showsolutionparams', 'on');
model.result('pg2').feature('con1').set('data', 'parent');
model.result.create('pg3', 'PlotGroup2D');
model.result('pg3').label([native2unicode(hex2dec({'6d' '41'}), 'unicode')  native2unicode(hex2dec({'4f' '53'}), 'unicode') ' 1 ' native2unicode(hex2dec({'76' '84'}), 'unicode')  native2unicode(hex2dec({'4f' '53'}), 'unicode')  native2unicode(hex2dec({'79' 'ef'}), 'unicode')  native2unicode(hex2dec({'52' '06'}), 'unicode')  native2unicode(hex2dec({'65' '70'}), 'unicode') ' (pf)']);
model.result('pg3').set('frametype', 'spatial');
model.result('pg3').feature.create('surf1', 'Surface');
model.result('pg3').feature('surf1').set('expr', 'pf.Vf1');
model.result('pg3').feature('surf1').set('smooth', 'internal');
model.result('pg3').feature('surf1').set('data', 'parent');
model.result('pg3').feature.create('con1', 'Contour');
model.result('pg3').feature('con1').set('expr', 'pf.Vf1');
model.result('pg3').feature('con1').set('levelmethod', 'levels');
model.result('pg3').feature('con1').set('levels', '0.5');
model.result('pg3').feature('con1').set('coloring', 'uniform');
model.result('pg3').feature('con1').set('colorlegend', false);
model.result('pg3').feature('con1').set('color', 'gray');
model.result('pg3').feature('con1').set('smooth', 'none');
model.result('pg3').feature('con1').set('data', 'parent');
model.result('pg1').run;
model.result('pg3').run;
model.result('pg3').feature('con1').stepFirst(0);
model.result('pg3').run;
model.result('pg3').feature('con1').stepNext(0);
model.result('pg3').run;
model.result('pg3').feature('con1').stepNext(0);
model.result('pg3').run;
model.result.export.create('anim1', 'Animation');
model.result.export('anim1').set('target', 'file');
model.result.export('anim1').set('plotgroup', 'pg3');
model.result.export('anim1').set('giffilename', 'D:\BaiduNetdiskDownload\Untitled1.gif');
model.result.export('anim1').run;

out = model;
