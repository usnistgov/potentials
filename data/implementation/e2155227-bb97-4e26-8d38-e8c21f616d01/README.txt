The files in this directory contain simple tabulations of the potential functions
- "pFeFe.spt" contains the FeFe pair interaction
- "pCrCr.spt" contains the CrCr pair interaction
- "pFeCr.spt" contains the FeCr pair interaction
- "rhoFe.spt" contains the d-density function for Fe
- "rhoCr.spt" contains the d-density function for Cr
- "rhoFeCr.spt" contains the s-density function for FeCr
- "Fd_Fe.spt" contains the d-embedding term for Fe
- "Fd_Cr.spt" contains the d-embedding term for Cr
No tabulation of the s-embedding terms is provided due to the singular slope in the origin. So care should be exercised if used in tabular form. We recommend to hard code the expressions for the s-embedding terms.
The s-embedding term is parameterized as:
Fs = A1 * sqrt(rho) + A2 * rho**2
- Coefficients for Fe: A1 = -0.217009784 and A2 = 0.388002579
- Coefficients for Cr: A1 = -0.00977557632 and A2 = 0.374570104
For further questions please contact gbonny@sckcen.be, pasianot@cnea.gov.ar, lmalerba@sckcen.be or dterenty@sckcen.be
