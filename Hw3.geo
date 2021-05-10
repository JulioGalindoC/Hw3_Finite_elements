SetFactory("OpenCASCADE");

L = 8.0;
H = 2.0;
r = 1.0;

Point(1) = {-L, -H, 0, 1.0};
Point(2) = {L, -H, 0, 1.0};
Point(3) = {L, H, 0, 1.0};
Point(4) = {-L, H, 0, 1.0};

Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};
Curve Loop(1) = {1, 2, 3, 4};

Plane Surface(1) = {1};

Extrude {-2.0, 0, 0} {
	Curve{4};
}

Extrude {2.0, 0, 0} {
	Curve{2};
}

Circle(11) = {0, 0, 0, r, 0, 2*Pi};

Curve Loop(4) = {11};

Plane Surface(4) = {4};

BooleanDifference{ Surface{1}; Delete; }{ Surface{4}; Delete; }

Physical Curve("Empotrado") = {7};
Physical Curve("BordeNatural") = {10};
Physical Surface("Extremos") = {2, 3};
Physical Surface("Placa") = {1};

Transfinite Curve {11} = 50 Using Progression 1;
