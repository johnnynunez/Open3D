#include "numeric.h"
#include <limits>

template<typename T> int check(const char* label) {
    T A[9]={0,1,0,1,0,0,0,0,1};
    T b[3]={1,3,6};
    T x[3]={};
    open3d::core::linalg::kernel::solve_svd3x3(A,b,x);
    double err=0;
    const T want[3]={3,1,6};
    for(int i=0;i<3;i++) { if(!std::isfinite(x[i])) err=std::numeric_limits<double>::infinity(); else err=std::max(err,std::abs(double(x[i]-want[i]))); }
    std::printf("%s x=[%.17g,%.17g,%.17g] max_error=%.17g\n",label,double(x[0]),double(x[1]),double(x[2]),err);
    return err<=1e-5 ? 0:1;
}
template<typename T> int spd(const char* label) {
    int failures=0;
    for(double scale : {0.01,1.0,100.0}) {
        T A[9]={T(4*scale),T(scale),T(.5*scale),T(scale),T(3*scale),T(.2*scale),T(.5*scale),T(.2*scale),T(2*scale)};
        T want[3]={1,-2,3},b[3]={},x[3]={};
        for(int i=0;i<3;i++) for(int j=0;j<3;j++) b[i]+=A[3*i+j]*want[j];
        open3d::core::linalg::kernel::solve_svd3x3(A,b,x);
        double err=0;
        for(int i=0;i<3;i++) { if(!std::isfinite(x[i])) err=std::numeric_limits<double>::infinity(); else err=std::max(err,std::abs(double(x[i]-want[i]))); }
        std::printf("%s SPD scale=%g max_error=%.17g\n",label,scale,err);
        if(err>1e-5) failures++;
    }
    return failures;
}
int main() { int f=check<float>("Float32"),d=check<double>("Float64"); return f+d+spd<float>("Float32")+spd<double>("Float64"); }
