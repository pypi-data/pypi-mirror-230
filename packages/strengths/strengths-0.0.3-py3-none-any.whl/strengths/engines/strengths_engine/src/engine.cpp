#include <iostream>
#include <random>
#include "SimulationAlgorithm3DBase.hpp"
#include "Euler3D.hpp"
#include "TauLeap3D.hpp"
#include "Gillespie3D.hpp"
#include <chrono>


template <typename T_in, typename T_out>
std::vector<T_out> ConvertVector(std::vector<T_in> & v_in)
    {
    std::vector<T_out> v_out(v_in.size());
    for(size_t i=0; i<v_in.size(); i++)
        {
        v_out[i] = static_cast<T_out>(v_in[i]);
        }
    return v_out;
    }

template<typename T_out, typename T_in> std::vector<T_out> MkVec(T_in * a, int len, bool floor_values = false)
    {
    std::vector<T_out> v(len);
    for(int i=0;i<len;i++)
        {
        v[i] = static_cast<T_out>(a[i]);
        if(floor_values)
            v[i] = floor(v[i]);
        }
    return v;
    }

SimulationAlgorithm3DBase * global_algo;

template<typename T> std::vector<T> SpeciesFirstToMeshFirstArray(std::vector<T> species_first_array, int n_species, int n_meshes)
    {
    std::vector<T> mesh_first_array(species_first_array.size());

    for(int s=0;s<n_species;s++)
        for(int i=0;i<n_meshes;i++)
            mesh_first_array[i*n_species+s] = species_first_array[s*n_meshes+i];
    return mesh_first_array;
    }

bool CompareStr(const char * str1, const char * str2)
    {
    return (std::string(str1) == std::string(str2));
    }

extern "C" int Initialize3D (
    int w,               //system width
    int h,               //system height
    int d,               //system depth
    int n_species,       //number of species
    int n_reactions,     //number of reactions
    int n_env,           //number of environments
    double * mesh_state, //species quantities
                         //size N*width*height*depth
                         //species first array : x = [species[depth[height[width]]]] or [species[mesh]]
    int *    mesh_chstt, //species chemostat flag
                         //size N*width*height*depth
                         //species first array : x = [species[depth[height[width]]]] or [species[mesh]]
    int *    mesh_env,   //species chemostat flag //size N*width*height*depth
    double mesh_vol,     //volume of a square mesh
    double * k,          //reaction rates //size M
    int * sub,           //N*M substrate matrix // (rows * columns) //size N*M
    int * sto,           //N*M stoechiometry matrix //size N*M
    int * r_env,         //reactions environmenrs
    double * D,          //diffusion coefficient for each species in each mesh type
    int sample_n,        //number of sample timepoints
    double * sample_t,   //sample timepoints //size sample_n
    double time_step,    //time step
    int seed,            //rng seed
    const char * option  //option
    )
    //return codes :
    //  0 : success
    //  1 : invalid option
    {
    int n_meshes = w*h*d;

    if      (CompareStr(option, "gillespie")) global_algo = new Gillespie3D();
    else if (CompareStr(option, "tauleap"))   global_algo = new TauLeap3D();
    else if (CompareStr(option, "euler"))     global_algo = new Euler3D();
    else return 1;

    bool floor_state = (CompareStr(option, "tauleap") || CompareStr(option, "gillespie")) ? true : false;

    global_algo->Init(
          w,
          h,
          d,
          n_species,
          n_reactions,
          n_env,
          SpeciesFirstToMeshFirstArray(MkVec<double, double>(mesh_state, n_meshes*n_species, floor_state),
                                       n_species,
                                       n_meshes), //species first to mesh first
          SpeciesFirstToMeshFirstArray(MkVec<int,    int   >(mesh_chstt, n_meshes*n_species),
                                       n_species,
                                       n_meshes), //species first to mesh first
          MkVec<int,    int   >(mesh_env, n_meshes),
          mesh_vol,
          MkVec<double, double>(k, n_reactions),
          MkVec<double, int   >(sub, n_species*n_reactions),
          MkVec<double, int   >(sto, n_species*n_reactions),
          MkVec<int,    int   >(r_env, n_reactions*n_env),
          MkVec<double, double>(D, n_species*n_env),
          sample_n,
          MkVec<double, double>(sample_t, sample_n),
          time_step,
          seed
          );

    return 0;
    }

extern "C" int Run  (
    int breathe_dt
    )
    {
    bool unfinished = true;
    auto t0 = std::chrono::system_clock::now();
    for(;;)
        {
        unfinished = global_algo->Iterate();
        int dt = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now() - t0).count();
        if(!unfinished || dt>=breathe_dt)
            break;
        }
    return unfinished;
    }

extern "C" double GetProgress()
    {
    //return t/tmax
    return global_algo->GetProgress();
    }

extern "C" int GetOutput(double * trajectory_data)
    {

    int n_samples = global_algo->NSamples();
    int n_species = global_algo->NSpecies();
    int n_meshes  = global_algo->NMeshes();

    std::vector<std::vector<double>> & trajectory_data_vec = global_algo->GetTrajectoryMatrix();
    for(int n=0;n<n_samples;n++)
        {
        for(int s=0;s<n_species;s++)
            {
            for(int i=0; i<n_meshes; i++)
                {
                //mesh first to species first
                trajectory_data[n*n_meshes*n_species+ s*n_meshes + i] = trajectory_data_vec[n][i*n_species+s];
                }
            }
        }
    return 0;
    }

extern "C" int Finalize ()
    {
    delete global_algo;
    return 0;
    }
